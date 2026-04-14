<template>
  <div
    :class="['message-item', String(message.sender_id) === String(currentUserId) ? 'message-sent' : 'message-received']"
  >
    <div v-if="message.msg_type === 1" class="message-content text-message">
      {{ message.content }}
    </div>

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

    <div v-else class="message-content other-message">
      {{ message.content }}
    </div>

    <div class="message-time">{{ formatTime(message.create_time) }}</div>
  </div>
</template>

<script>
import { downloadFile as downloadEncryptedFile } from '@/api/encry/file'
import { downloadShare, downloadShareByFile, getSharedByMe, getSharedToMe } from '@/api/encry/share'

export default {
  name: 'MessageItem',
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
    isSentByCurrentUser() {
      return String(this.message.sender_id) === String(this.currentUserId)
    },
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
      if (filePath.startsWith('发送了文件:')) {
        return filePath.split(':').slice(1).join(':').trim() || '未知文件'
      }
      const parts = filePath.replace(/\\/g, '/').split('/')
      return parts[parts.length - 1]
    },
    getFileSize(fileId) {
      return fileId ? '点击下载' : '历史记录'
    },
    async downloadSentFile(fileName) {
      if (this.message.file_id) {
        await downloadEncryptedFile(this.message.file_id, fileName)
        return
      }

      const response = await getSharedByMe({ page: 1, page_size: 200 })
      const rows = (response.data && response.data.rows) || []
      const match = rows.find(item =>
        String(item.target_user_id) === String(this.message.receiver_id) &&
        item.file_name === fileName
      )

      if (!match || !match.file_id) {
        throw new Error('未找到对应的文件记录，请重新发送一次文件')
      }

      await downloadEncryptedFile(match.file_id, fileName)
    },
    async downloadReceivedFile(fileName) {
      if (this.message.file_id) {
        await downloadShareByFile(this.message.file_id, fileName)
        return
      }

      const response = await getSharedToMe({ page: 1, page_size: 200 })
      const rows = (response.data && response.data.rows) || []
      const match = rows.find(item =>
        String(item.owner_id) === String(this.message.sender_id) &&
        item.file_name === fileName
      )

      if (!match) {
        throw new Error('未找到对应的分享记录，请让对方重新发送一次文件')
      }

      await downloadShare(match.share_id, fileName)
    },
    async downloadFile() {
      try {
        const fileName = this.getFileName(this.message.content)
        if (this.isSentByCurrentUser()) {
          await this.downloadSentFile(fileName)
        } else {
          await this.downloadReceivedFile(fileName)
        }
      } catch (error) {
        this.$message.error(error.message || '下载失败')
      }
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
