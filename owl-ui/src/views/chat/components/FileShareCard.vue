<template>
  <div class="file-share-card">
    <div class="file-icon">
      <i class="el-icon-document"></i>
    </div>
    <div class="file-info">
      <div class="file-name">{{ fileName }}</div>
      <div class="file-meta">
        <span class="file-size">{{ formatFileSize(fileSize) }}</span>
        <span v-if="senderName" class="sender-name">分享者: {{ senderName }}</span>
      </div>
    </div>
    <div class="file-actions">
      <el-button 
        type="primary" 
        size="small" 
        @click="handleDownload"
        :loading="downloading"
      >
        <i class="el-icon-download"></i> 下载
      </el-button>
    </div>
  </div>
</template>

<script>
import { downloadShare } from '@/api/encry/share'

export default {
  name: 'FileShareCard',
  props: {
    shareId: {
      type: Number,
      required: true
    },
    fileName: {
      type: String,
      default: '未知文件'
    },
    fileSize: {
      type: Number,
      default: 0
    },
    senderName: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      downloading: false
    }
  },
  methods: {
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    async handleDownload() {
      this.downloading = true
      try {
        await downloadShare(this.shareId)
      } catch (error) {
        this.$message.error('下载失败：' + (error.message || '未知错误'))
      } finally {
        this.downloading = false
      }
    }
  }
}
</script>

<style scoped>
.file-share-card {
  display: flex;
  align-items: center;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 8px;
  margin: 8px 0;
  transition: all 0.3s ease;
}

.file-share-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.file-icon {
  font-size: 24px;
  color: #409eff;
  margin-right: 12px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #ecf5ff;
  border-radius: 4px;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-meta {
  font-size: 12px;
  color: #909399;
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-actions {
  margin-left: 16px;
}
</style>
