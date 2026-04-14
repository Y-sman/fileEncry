<template>
  <div class="app-container">
    <el-card>
      <template slot="header">
        <div class="card-header">
          <span>文件分享管理</span>
        </div>
      </template>
      
      <el-tabs v-model="activeTab" @tab-click="handleTabChange">
        <!-- 分享给我的 -->
        <el-tab-pane label="分享给我的" name="shared-to-me">
          <div class="table-container">
            <el-table :data="sharedToMeList" style="width: 100%">
              <el-table-column prop="owner_name" label="分享者" width="120" />
              <el-table-column prop="file_name" label="文件名">
                <template slot-scope="scope">
                  <span>{{ scope.row.file_name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="文件大小" width="100">
                <template slot-scope="scope">
                  <span>{{ formatFileSize(scope.row.file_size) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="create_time" label="分享时间" width="180" />
              <el-table-column label="操作" width="100" fixed="right">
                <template slot-scope="scope">
                  <el-button 
                    type="primary" 
                    size="small" 
                    @click="downloadSharedFile(scope.row)"
                    :loading="downloadingShareId === scope.row.share_id"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="sharedToMeTotal === 0" class="empty-state">
              <el-empty description="暂无分享记录" />
            </div>
            
            <div v-else class="pagination-container">
              <el-pagination
                :current-page="sharedToMePage"
                :page-size="pageSize"
                :total="sharedToMeTotal"
                layout="total, prev, pager, next"
                @current-change="handleSharedToMePageChange"
              />
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 我分享的 -->
        <el-tab-pane label="我分享的" name="shared-by-me">
          <div class="table-container">
            <el-table :data="sharedByMeList" style="width: 100%">
              <el-table-column prop="target_user_name" label="接收者" width="120" />
              <el-table-column prop="file_name" label="文件名">
                <template slot-scope="scope">
                  <span>{{ scope.row.file_name }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="file_size" label="文件大小" width="100">
                <template slot-scope="scope">
                  <span>{{ formatFileSize(scope.row.file_size) }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="create_time" label="分享时间" width="180" />
              <el-table-column prop="status" label="状态" width="80">
                <template slot-scope="scope">
                  <el-tag :type="scope.row.status === 0 ? 'success' : 'info'">
                    {{ scope.row.status === 0 ? '有效' : '已撤销' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" fixed="right">
                <template slot-scope="scope">
                  <el-button 
                    type="danger" 
                    size="small" 
                    @click="revokeShare(scope.row.share_id)"
                    :loading="revokingShareId === scope.row.share_id"
                    :disabled="scope.row.status !== 0"
                  >
                    撤销
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div v-if="sharedByMeTotal === 0" class="empty-state">
              <el-empty description="暂无分享记录" />
            </div>
            
            <div v-else class="pagination-container">
              <el-pagination
                :current-page="sharedByMePage"
                :page-size="pageSize"
                :total="sharedByMeTotal"
                layout="total, prev, pager, next"
                @current-change="handleSharedByMePageChange"
              />
            </div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script>
import { getSharedToMe, getSharedByMe, revokeShare, downloadShare } from '@/api/encry/share'

export default {
  name: 'EncryShare',
  data() {
    return {
      activeTab: 'shared-to-me',
      pageSize: 10,
      
      // 分享给我的
      sharedToMePage: 1,
      sharedToMeList: [],
      sharedToMeTotal: 0,
      
      // 我分享的
      sharedByMePage: 1,
      sharedByMeList: [],
      sharedByMeTotal: 0,
      
      // 加载状态
      downloadingShareId: null,
      revokingShareId: null
    }
  },
  created() {
    this.loadSharedToMe()
  },
  activated() {
    // 页面重新激活时刷新数据
    if (this.activeTab === 'shared-to-me') {
      this.loadSharedToMe()
    } else {
      this.loadSharedByMe()
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
    
    handleTabChange(tab) {
      // 兼容 Element UI 的 tab-click 事件，直接使用 tab.name
      const tabName = tab.name || (tab.props && tab.props.name)
      if (tabName === 'shared-to-me') {
        this.loadSharedToMe()
      } else if (tabName === 'shared-by-me') {
        this.loadSharedByMe()
      }
    },
    
    async loadSharedToMe() {
      try {
        const response = await getSharedToMe({
          page: this.sharedToMePage,
          page_size: this.pageSize
        })
        if (response.code === 200) {
          this.sharedToMeList = response.data.rows
          this.sharedToMeTotal = response.data.total
        }
      } catch (error) {
        console.error('获取分享给我的文件失败:', error)
        this.$message.error('获取分享记录失败')
      }
    },
    
    async loadSharedByMe() {
      try {
        const response = await getSharedByMe({
          page: this.sharedByMePage,
          page_size: this.pageSize
        })
        if (response.code === 200) {
          this.sharedByMeList = response.data.rows
          this.sharedByMeTotal = response.data.total
        }
      } catch (error) {
        console.error('获取我分享的文件失败:', error)
        this.$message.error('获取分享记录失败')
      }
    },
    
    handleSharedToMePageChange(page) {
      this.sharedToMePage = page
      this.loadSharedToMe()
    },
    
    handleSharedByMePageChange(page) {
      this.sharedByMePage = page
      this.loadSharedByMe()
    },
    
    async downloadSharedFile(row) {
      const shareId = row.share_id
      const fileName = row.file_name || ''
      this.downloadingShareId = shareId
      try {
        await downloadShare(shareId, fileName)
      } catch (error) {
        console.error('下载文件失败:', error)
        this.$message.error('下载失败：' + (error.message || '未知错误'))
      } finally {
        this.downloadingShareId = null
      }
    },
    
    async revokeShare(shareId) {
      this.revokingShareId = shareId
      try {
        const response = await revokeShare(shareId)
        if (response.code === 200) {
          this.$message.success('撤销分享成功')
          this.loadSharedByMe()
        } else {
          this.$message.error('撤销分享失败')
        }
      } catch (error) {
        console.error('撤销分享失败:', error)
        this.$message.error('撤销失败：' + (error.message || '未知错误'))
      } finally {
        this.revokingShareId = null
      }
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

.table-container {
  margin-top: 20px;
}

.empty-state {
  padding: 40px 0;
  display: flex;
  justify-content: center;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
