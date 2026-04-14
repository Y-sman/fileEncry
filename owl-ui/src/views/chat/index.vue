<template>
  <div class="app-container">
    <el-card>
      <template slot="header">
        <div class="card-header">
          <span>聊天</span>
        </div>
      </template>
      <div class="chat-container">
        <!-- 左侧好友列表 -->
        <div class="friend-list-container">
          <friend-list
            :friends="friends"
            :active-friend-id="activeFriendId"
            @select="selectFriend"
          />
        </div>
        
        <!-- 右侧聊天窗口 -->
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
      
      <!-- 分享文件弹窗 -->
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
      
      <!-- 文件选择对话框 -->
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
import { getSessions, getHistory, markAsRead } from '@/api/chat'
import { getFriendList } from '@/api/friend'
import socketClient from '@/utils/socket'
import { getToken } from '@/utils/auth'
import { getUserProfile } from '@/api/system/user'
// import { getFileList } from '@/api/encry/file'
import { listFile } from '@/api/encry/file'
import { getUserPublicKey, uploadEncryptedFile } from '@/api/encry/key'
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
      messages: {}, // 按好友ID存储消息
      currentUserId: 0,
      loadingMore: false,
      page: 1,
      pageSize: 20,
      // 文件分享相关
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
      // 获取当前用户信息
      await this.getCurrentUserInfo()
      // 获取好友列表
      await this.getFriends()
    },
    async getCurrentUserInfo() {
      try {
        const response = await getUserProfile()
        if (response.code === 200) {
          // 后端返回驼峰命名 userId
          this.currentUserId = response.data.userId
          console.log('当前用户ID:', this.currentUserId)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    },
    async getFriends() {
      try {
        const response = await getFriendList()
        if (response.code === 200) {
          // 为每个好友添加 online 字段，默认为 false
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
      // 获取聊天历史
      await this.getChatHistory(friend.user_id)
      // 标记消息为已读
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
          // 更新好友列表中的未读计数
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
        // 通过 WebSocket 发送消息
        await socketClient.sendMessage(
          messageData.receiver_id,
          messageData.content,
          messageData.msg_type
        )
        
        // 本地添加消息
        const newMessage = {
          id: Date.now(),
          sender_id: this.currentUserId,
          receiver_id: messageData.receiver_id,
          content: messageData.content,
          msg_type: messageData.msg_type,
          is_read: 1,
          create_time: new Date()
        }
        
        if (!this.messages[messageData.receiver_id]) {
          this.$set(this.messages, messageData.receiver_id, [])
        }
        this.messages[messageData.receiver_id].push(newMessage)
        
        // 更新好友列表中的最后消息 - 使用 Vue.set 确保响应式
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
      // 实际应用中，这里应该打开文件选择对话框
      console.log('选择文件')
    },
    async openShareDialog() {
      // 获取用户的文件列表
      try {
        const response = await listFile({ pageNum: 1, pageSize: 50 })
        if (response.code === 200 && response.rows) {
          this.fileList = response.rows
          this.selectedFileId = null
          // 打开文件选择对话框
          this.fileSelectDialogVisible = true
        } else {
          console.error('获取文件列表失败: 数据格式不正确')
          this.$message.error('获取文件列表失败: 数据格式不正确')
        }
      } catch (error) {
        console.error('获取文件列表失败:', error)
        this.$message.error('获取文件列表失败')
      }
    },
    confirmFileSelect() {
      if (this.selectedFileId) {
        const file = this.fileList.find(f => f.fileId === this.selectedFileId)
        if (file) {
          this.selectedFile = file
          this.fileSelectDialogVisible = false
          this.shareDialogVisible = true
        } else {
          this.$message.error('文件不存在')
        }
      } else {
        this.$message.error('请选择文件')
      }
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
        // 显示加载提示
        loading = this.$loading({
          lock: true,
          text: '正在加密发送文件...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })
        
        // 上传加密文件
        const response = await uploadEncryptedFile(data.file, data.receiver_id)
        
        if (response.code === 200) {
          // 发送消息通知接收者
          await this.sendMessage({
            receiver_id: data.receiver_id,
            content: `发送了文件: ${data.file.name}`,
            msg_type: 2 // 文件消息
          })
          
          this.$message.success('文件加密发送成功')
        } else {
          this.$message.error('文件发送失败: ' + (response.msg || '未知错误'))
        }
      } catch (error) {
        console.error('文件加密发送失败:', error)
        this.$message.error('文件加密发送失败: ' + (error.message || '未知错误'))
      } finally {
        // 关闭加载提示
        if (loading) {
          loading.close()
        }
      }
    },
    connectWebSocket() {
      // 建立 WebSocket 连接
      socketClient.connect().then(() => {
        console.log('WebSocket 连接成功')
        
        // 监听接收消息
        socketClient.onReceiveMessage((message) => {
          // 添加消息到对应好友的消息列表 - 使用 Vue.set 确保响应式
          if (!this.messages[message.sender_id]) {
            this.$set(this.messages, message.sender_id, [])
          }
          this.messages[message.sender_id].push(message)
          
          // 更新好友列表中的最后消息和未读计数 - 使用 Vue.set 确保响应式
          const friendIndex = this.friends.findIndex(f => f.user_id === message.sender_id)
          if (friendIndex !== -1) {
            this.$set(this.friends[friendIndex], 'last_msg_content', message.content)
            this.$set(this.friends[friendIndex], 'last_msg_time', message.create_time)

            // 如果不是当前聊天的好友，增加未读计数
            if (this.activeFriendId !== message.sender_id) {
              const currentUnread = this.friends[friendIndex].unread_count || 0
              this.$set(this.friends[friendIndex], 'unread_count', currentUnread + 1)
            }
          }
        })
        
        // 监听好友上线
        socketClient.onFriendOnline((data) => {
          console.log('好友上线:', data)
          const friendIndex = this.friends.findIndex(f => f.user_id === data.user_id)
          if (friendIndex !== -1) {
            // 使用 Vue.set 确保响应式更新
            this.$set(this.friends[friendIndex], 'online', true)
          }
        })

        // 监听好友下线
        socketClient.onFriendOffline((data) => {
          console.log('好友下线:', data)
          const friendIndex = this.friends.findIndex(f => f.user_id === data.user_id)
          if (friendIndex !== -1) {
            // 使用 Vue.set 确保响应式更新
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