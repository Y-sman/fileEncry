<template>
  <div class="app-container">
    <el-card>
      <template slot="header">
        <div class="card-header">
          <span>聊天</span>
        </div>
      </template>
      <div class="chat-container">
        <div class="friend-list-container">
          <friend-list
            :friends="friends"
            :active-friend-id="activeFriendId"
            @select="selectFriend"
          />
        </div>

        <div class="chat-window-container">
          <chat-window
            v-if="activeFriend"
            :active-friend="activeFriend"
            :messages="currentMessages"
            :current-user-id="currentUserId"
            :loading-more="loadingMore"
            @send-message="sendMessage"
            @load-more="loadMore"
            @select-file="selectFile"
            @open-share-dialog="openShareDialog"
            @encrypt-send-file="encryptSendFile"
          />
          <div class="chat-empty" v-else>
            <el-empty description="选择一个好友开始聊天" />
          </div>
        </div>
      </div>

      <ShareFileDialog
        :visible.sync="shareDialogVisible"
        :file="{
          fileId: selectedFile ? selectedFile.fileId : 0,
          fileName: selectedFile ? selectedFile.originalName : '',
          fileSize: selectedFile ? selectedFile.fileSize : 0
        }"
        @update:visible="handleShareDialogVisible"
        @success="handleShareSuccess"
      />

      <el-dialog
        title="选择文件"
        :visible.sync="fileSelectDialogVisible"
        width="500px"
      >
        <el-select
          v-model="selectedFileId"
          placeholder="请选择要分享的文件"
          style="width: 100%;"
          :key="fileList.length"
        >
          <el-option
            v-for="file in fileList"
            :key="file.fileId"
            :label="file.originalName"
            :value="file.fileId"
          >
            <div style="display: flex; justify-content: space-between;">
              <span>{{ file.originalName }}</span>
              <span style="color: #999; font-size: 12px;">{{ (file.fileSize / 1024).toFixed(2) }} KB</span>
            </div>
          </el-option>
        </el-select>
        <span slot="footer" class="dialog-footer">
          <el-button @click="fileSelectDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmFileSelect">确定</el-button>
        </span>
      </el-dialog>
    </el-card>
  </div>
</template>

<script>
import FriendList from '@/components/Chat/FriendList'
import ChatWindow from '@/components/Chat/ChatWindow'
import { getHistory, markAsRead } from '@/api/chat'
import { getFriendList } from '@/api/friend'
import socketClient from '@/utils/socket'
import { getUserProfile } from '@/api/system/user'
import { listFile } from '@/api/encry/file'
import { uploadEncryptedFile } from '@/api/encry/key'
import ShareFileDialog from '@/components/ShareFileDialog'

export default {
  name: 'Chat',
  components: {
    FriendList,
    ChatWindow,
    ShareFileDialog
  },
  data() {
    return {
      friends: [],
      activeFriendId: null,
      messages: {},
      currentUserId: 0,
      loadingMore: false,
      page: 1,
      pageSize: 20,
      shareDialogVisible: false,
      fileList: [],
      selectedFile: null,
      fileSelectDialogVisible: false,
      selectedFileId: null
    }
  },
  computed: {
    currentMessages() {
      return this.messages[this.activeFriendId] || []
    },
    activeFriend() {
      if (!this.activeFriendId) return null
      return this.friends.find(f => f.user_id === this.activeFriendId) || null
    }
  },
  created() {
    this.init()
  },
  mounted() {
    this.connectWebSocket()
  },
  beforeDestroy() {
    socketClient.disconnect()
  },
  methods: {
    async init() {
      await this.getCurrentUserInfo()
      await this.getFriends()
    },
    async getCurrentUserInfo() {
      try {
        const response = await getUserProfile()
        if (response.code === 200) {
          this.currentUserId = response.data.userId
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    async getFriends() {
      try {
        const response = await getFriendList()
        if (response.code === 200) {
          this.friends = response.data.map(friend => ({
            ...friend,
            online: false
          }))
        }
      } catch (error) {
        console.error('获取好友列表失败:', error)
      }
    },
    async selectFriend(friend) {
      this.activeFriendId = friend.user_id
      this.page = 1
      await this.getChatHistory(friend.user_id)
      await this.markMessagesAsRead(friend.user_id)
    },
    async getChatHistory(friendId) {
      try {
        const response = await getHistory(friendId, this.page, this.pageSize)
        if (response.code === 200) {
          if (this.page === 1) {
            this.$set(this.messages, friendId, response.data)
          } else {
            const existingMessages = this.messages[friendId] || []
            this.$set(this.messages, friendId, [...response.data, ...existingMessages])
          }
        }
      } catch (error) {
        console.error('获取聊天历史失败:', error)
      } finally {
        this.loadingMore = false
      }
    },
    async markMessagesAsRead(friendId) {
      try {
        const response = await markAsRead(friendId)
        if (response.code === 200) {
          const friendIndex = this.friends.findIndex(f => f.user_id === friendId)
          if (friendIndex !== -1) {
            this.friends[friendIndex].unread_count = 0
          }
        }
      } catch (error) {
        console.error('标记消息已读失败:', error)
      }
    },
    async sendMessage(messageData) {
      try {
        await socketClient.sendMessage(
          messageData.receiver_id,
          messageData.content,
          messageData.msg_type,
          messageData.file_id || null
        )

        const newMessage = {
          id: Date.now(),
          sender_id: this.currentUserId,
          receiver_id: messageData.receiver_id,
          content: messageData.content,
          msg_type: messageData.msg_type,
          file_id: messageData.file_id || null,
          is_read: 1,
          create_time: new Date()
        }

        if (!this.messages[messageData.receiver_id]) {
          this.$set(this.messages, messageData.receiver_id, [])
        }
        this.messages[messageData.receiver_id].push(newMessage)

        const friendIndex = this.friends.findIndex(f => f.user_id === messageData.receiver_id)
        if (friendIndex !== -1) {
          this.$set(this.friends[friendIndex], 'last_msg_content', messageData.content)
          this.$set(this.friends[friendIndex], 'last_msg_time', new Date())
        }
      } catch (error) {
        console.error('发送消息失败:', error)
        this.$message.error('发送消息失败')
      }
    },
    loadMore() {
      if (this.loadingMore) return
      this.loadingMore = true
      this.page++
      this.getChatHistory(this.activeFriendId)
    },
    selectFile() {
      console.log('选择文件')
    },
    async openShareDialog() {
      try {
        const response = await listFile({ pageNum: 1, pageSize: 50 })
        if (response.code === 200 && response.rows) {
          this.fileList = response.rows
          this.selectedFileId = null
          this.fileSelectDialogVisible = true
        } else {
          this.$message.error('获取文件列表失败')
        }
      } catch (error) {
        console.error('获取文件列表失败:', error)
        this.$message.error('获取文件列表失败')
      }
    },
    confirmFileSelect() {
      if (!this.selectedFileId) {
        this.$message.error('请选择文件')
        return
      }

      const file = this.fileList.find(f => f.fileId === this.selectedFileId)
      if (!file) {
        this.$message.error('文件不存在')
        return
      }

      this.selectedFile = file
      this.fileSelectDialogVisible = false
      this.shareDialogVisible = true
    },
    handleShareDialogVisible(visible) {
      this.shareDialogVisible = visible
    },
    handleShareSuccess(count) {
      this.$message.success(`成功分享给 ${count} 位好友`)
    },
    async encryptSendFile(data) {
      let loading = null
      try {
        loading = this.$loading({
          lock: true,
          text: '正在加密发送文件...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        const response = await uploadEncryptedFile(data.file, data.receiver_id)
        const payload = response.data || {}

        if (response.code === 200) {
          await this.sendMessage({
            receiver_id: data.receiver_id,
            content: data.file.name,
            msg_type: 2,
            file_id: payload.file_id || null
          })

          this.$message.success('文件加密发送成功')
        } else {
          this.$message.error('文件发送失败: ' + (response.msg || '未知错误'))
        }
      } catch (error) {
        console.error('文件加密发送失败:', error)
        this.$message.error('文件加密发送失败: ' + (error.message || '未知错误'))
      } finally {
        if (loading) {
          loading.close()
        }
      }
    },
    connectWebSocket() {
      socketClient.connect().then(() => {
        socketClient.onReceiveMessage((message) => {
          if (!this.messages[message.sender_id]) {
            this.$set(this.messages, message.sender_id, [])
          }
          this.messages[message.sender_id].push(message)

          const friendIndex = this.friends.findIndex(f => f.user_id === message.sender_id)
          if (friendIndex !== -1) {
            this.$set(this.friends[friendIndex], 'last_msg_content', message.content)
            this.$set(this.friends[friendIndex], 'last_msg_time', message.create_time)

            if (this.activeFriendId !== message.sender_id) {
              const currentUnread = this.friends[friendIndex].unread_count || 0
              this.$set(this.friends[friendIndex], 'unread_count', currentUnread + 1)
            }
          }
        })

        socketClient.onFriendOnline((data) => {
          const friendIndex = this.friends.findIndex(f => f.user_id === data.user_id)
          if (friendIndex !== -1) {
            this.$set(this.friends[friendIndex], 'online', true)
          }
        })

        socketClient.onFriendOffline((data) => {
          const friendIndex = this.friends.findIndex(f => f.user_id === data.user_id)
          if (friendIndex !== -1) {
            this.$set(this.friends[friendIndex], 'online', false)
          }
        })
      }).catch(error => {
        console.error('WebSocket 连接失败:', error)
      })
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-container {
  display: flex;
  height: 600px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

.friend-list-container {
  width: 220px;
  height: 100%;
  flex-shrink: 0;
}

.chat-window-container {
  flex: 1;
  height: 100%;
  min-width: 0;
}

.chat-empty {
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #fafafa;
}
</style>
