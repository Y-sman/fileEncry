<template>
  <el-dialog
    :title="'分享文件 - ' + file.fileName"
    :visible.sync="visible"
    width="500px"
    @close="handleClose"
  >
    <div class="dialog-content">
      <!-- 文件信息 -->
      <div class="file-info">
        <div class="file-item">
          <span class="label">文件名：</span>
          <span class="value">{{ file.fileName }}</span>
        </div>
        <div class="file-item">
          <span class="label">文件大小：</span>
          <span class="value">{{ formatFileSize(file.fileSize) }}</span>
        </div>
      </div>
      
      <!-- 好友选择 -->
      <div class="friend-selection">
        <el-form>
          <el-form-item label="选择好友">
            <el-select
              v-model="selectedFriends"
              multiple
              placeholder="请选择要分享的好友"
              style="width: 100%"
              @change="handleFriendChange"
              :key="friendList.length"
            >
              <el-option
                v-for="friend in friendList"
                :key="friend.user_id"
                :label="friend.nick_name"
                :value="friend.user_id"
              >
                <div class="friend-option">
                  <span class="friend-name">{{ friend.nick_name }}</span>
                  <span class="friend-status" :class="{ online: friend.online }">
                    {{ friend.online ? '在线' : '离线' }}
                  </span>
                </div>
              </el-option>
            </el-select>
          </el-form-item>
        </el-form>
      </div>
    </div>
    
    <span slot="footer" class="dialog-footer">
      <el-button @click="handleClose">取消</el-button>
      <el-button 
        type="primary" 
        @click="handleShare" 
        :loading="sharing"
        :disabled="selectedFriends.length === 0"
      >
        确认分享
      </el-button>
    </span>
  </el-dialog>
</template>

<script>
import { getFriendList } from '@/api/friend'
import { shareFile } from '@/api/encry/share'

export default {
  name: 'ShareFileDialog',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    file: {
      type: Object,
      required: true,
      default: () => ({
        fileId: 0,
        fileName: '',
        fileSize: 0
      })
    }
  },
  data() {
    return {
      friendList: [],
      selectedFriends: [],
      sharing: false
    }
  },
  watch: {
    visible: {
      handler(newVal) {
        if (newVal) {
          this.loadFriends()
        } else {
          this.resetForm()
        }
      },
      immediate: true
    }
  },
  methods: {
    resetForm() {
      this.selectedFriends = []
      this.sharing = false
    },
    async loadFriends() {
      try {
        const response = await getFriendList()
        if (response.code === 200) {
          this.friendList = response.data
        }
      } catch (error) {
        this.$message.error('获取好友列表失败：' + (error.message || '未知错误'))
      }
    },
    formatFileSize(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    handleFriendChange() {
      // 好友选择变化时的处理
    },
    async handleShare() {
      if (this.selectedFriends.length === 0) {
        this.$message.warning('请选择要分享的好友')
        return
      }
      
      this.sharing = true
      let successCount = 0
      
      try {
        for (const targetUserId of this.selectedFriends) {
          const response = await shareFile(this.file.fileId, targetUserId)
          if (response.code === 200) {
            successCount++
          }
        }
        
        if (successCount > 0) {
          this.$message.success(`成功分享给 ${successCount} 位好友`)
          this.$emit('success', successCount)
          this.handleClose()
        } else {
          this.$message.error('分享失败')
        }
      } catch (error) {
        this.$message.error('分享失败：' + (error.message || '未知错误'))
      } finally {
        this.sharing = false
      }
    },
    handleClose() {
      this.$emit('update:visible', false)
      this.resetForm()
    }
  }
}
</script>

<style scoped>
.dialog-content {
  padding: 10px 0;
}

.file-info {
  background-color: #f5f7fa;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.file-item {
  display: flex;
  margin-bottom: 8px;
}

.file-item:last-child {
  margin-bottom: 0;
}

.label {
  width: 80px;
  font-weight: 500;
  color: #606266;
}

.value {
  flex: 1;
  color: #303133;
}

.friend-selection {
  margin-top: 20px;
}

.friend-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.friend-status {
  font-size: 12px;
  color: #909399;
}

.friend-status.online {
  color: #67c23a;
}

.dialog-footer {
  text-align: right;
}
</style>
