<template>
  <div class="chat-window">
    <div class="chat-header">
      <el-avatar :size="36">
        {{ activeFriend && activeFriend.nick_name ? activeFriend.nick_name.charAt(0) : '?' }}
      </el-avatar>
      <div class="chat-header-info">
        <div class="chat-header-name">{{ activeFriend && activeFriend.nick_name ? activeFriend.nick_name : '未知' }}</div>
        <div class="chat-header-status" v-if="activeFriend" :class="{ 'online': activeFriend.online, 'offline': !activeFriend.online }">
          {{ activeFriend.online ? '在线' : '离线' }}
        </div>
      </div>
    </div>
    
    <div class="chat-messages" ref="messagesContainer" @scroll="handleScroll">
      <div class="loading-more" v-if="loadingMore">
        <i class="el-icon-loading"></i>
        <span>加载更多...</span>
      </div>
      <message-item
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :current-user-id="currentUserId"
      />
    </div>
    
    <div class="chat-input">
      <div class="chat-input-actions">
        <el-button type="primary" icon="el-icon-upload" @click="triggerFileSelect">
          发送文件
        </el-button>
        <el-button type="success" icon="el-icon-share" @click="openShareDialog">
          分享文件
        </el-button>
      </div>
      <!-- 文件选择输入 -->
      <input 
        type="file" 
        ref="fileInput" 
        style="display: none" 
        @change="handleFileSelect"
      />
      <el-input
        v-model="inputMessage"
        type="textarea"
        placeholder="输入消息..."
        :rows="3"
        @keyup.enter.ctrl="sendMessage"
      ></el-input>
      <div class="chat-input-actions">
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
    
    <!-- 分享文件弹窗已移至父组件 -->
  </div>
</template>

<script>
import MessageItem from './MessageItem'

export default {
  name: 'ChatWindow',
  components: {
    MessageItem
  },
  props: {
    activeFriend: {
      type: Object,
      default: null
    },
    messages: {
      type: Array,
      default: () => []
    },
    currentUserId: {
      type: Number,
      default: 0
    },
    loadingMore: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      inputMessage: ''
    }
  },
  methods: {
    sendMessage() {
      if (!this.inputMessage.trim() || !this.activeFriend) {
        return
      }
      this.$emit('send-message', {
        receiver_id: this.activeFriend.user_id,
        content: this.inputMessage,
        msg_type: 1 // 文本消息
      })
      this.inputMessage = ''
    },
    handleScroll() {
      const container = this.$refs.messagesContainer
      if (container && container.scrollTop === 0) {
        this.$emit('load-more')
      }
    },
    triggerFileSelect() {
      this.$refs.fileInput.click()
    },
    async handleFileSelect(event) {
      const file = event.target.files[0]
      if (!file) return
      
      try {
        // 触发加密发送文件事件
        this.$emit('encrypt-send-file', {
          receiver_id: this.activeFriend.user_id,
          file: file
        })
      } catch (error) {
        console.error('文件处理失败:', error)
      } finally {
        // 重置文件输入
        event.target.value = ''
      }
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const container = this.$refs.messagesContainer
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    },
    openShareDialog() {
      // 这里需要获取当前用户的文件列表，让用户选择要分享的文件
      // 暂时先触发事件，由父组件处理
      this.$emit('open-share-dialog')
    },

  },
  watch: {
    messages() {
      this.scrollToBottom()
    }
  },
  mounted() {
    this.scrollToBottom()
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #e4e7ed;
  background-color: #f5f7fa;
}

.chat-header-info {
  margin-left: 10px;
  flex: 1;
}

.chat-header-name {
  font-weight: bold;
}

.chat-header-status {
  font-size: 12px;
}

.chat-header-status.online {
  color: #67c23a;
}

.chat-header-status.offline {
  color: #909399;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background-color: #fafafa;
  min-height: 0;
}

.loading-more {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px 0;
  color: #909399;
}

.chat-input {
  padding: 16px;
  border-top: 1px solid #e4e7ed;
  background-color: white;
}

.chat-input-actions {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.chat-input-actions:last-child {
  margin-bottom: 0;
  margin-top: 10px;
}
</style>