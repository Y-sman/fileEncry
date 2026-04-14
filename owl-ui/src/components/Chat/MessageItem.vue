<template>
  <div
    :class="['message-item', String(message.sender_id) === String(currentUserId) ? 'message-sent' : 'message-received']"
  >
    <!-- 文本消息 -->
    <div v-if="message.msg_type === 1" class="message-content text-message">
      {{ message.content }}
    </div>
    
    <!-- 文件消息 -->
    <div v-else-if="message.msg_type === 2" class="message-content file-message">
      <el-card shadow="hover">
        <div class="file-info">
          <i class="el-icon-document file-icon"></i>
          <div class="file-details">
            <div class="file-name">{{ getFileName(message.content) }}</div>
            <div class="file-size">{{ getFileSize(message.file_id) }}</div>
          </div>
          <el-button type="primary" size="small" @click="downloadFile">
            下载
          </el-button>
        </div>
      </el-card>
    </div>
    
    <!-- 其他类型消息 -->
    <div v-else class="message-content other-message">
      {{ message.content }}
    </div>
    
    <div class="message-time">{{ formatTime(message.create_time) }}</div>
  </div>
</template>

<script>
export default {
  name: 'MessageItem',
  components: {
  },
  props: {
    message: {
      type: Object,
      required: true
    },
    currentUserId: {
      type: Number,
      required: true
    }
  },
  methods: {
    formatTime(time) {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    },
    getFileName(filePath) {
      if (!filePath) return '未知文件'
      const parts = filePath.split('/')
      return parts[parts.length - 1]
    },
    getFileSize(fileId) {
      // 实际应用中，这里应该根据 fileId 从服务器获取文件大小
      return '未知大小'
    },
    downloadFile() {
      // 实际应用中，这里应该调用下载文件的 API
      console.log('下载文件:', this.message.file_id)
    }
  }
}
</script>

<style scoped>
.message-item {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-sent {
  align-items: flex-end;
  margin-left: auto;
}

.message-received {
  align-items: flex-start;
  margin-right: auto;
}

.message-content {
  padding: 10px 14px;
  border-radius: 18px;
  word-break: break-all;
}

.message-sent .text-message {
  background-color: #409eff;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-received .text-message {
  background-color: white;
  color: #303133;
  border-bottom-left-radius: 4px;
  border: 1px solid #e4e7ed;
}

.file-message {
  padding: 0;
  border-radius: 8px;
  overflow: hidden;
}

.file-info {
  display: flex;
  align-items: center;
  padding: 10px;
}

.file-icon {
  font-size: 24px;
  color: #409eff;
  margin-right: 10px;
}

.file-details {
  flex: 1;
  overflow: hidden;
}

.file-name {
  font-weight: bold;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-size {
  font-size: 12px;
  color: #909399;
}

.other-message {
  background-color: #f0f0f0;
  color: #303133;
  border-radius: 8px;
}

.message-time {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>