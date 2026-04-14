<template>
  <div class="app-container">
    <!-- 搜索用户区域 -->
    <el-card class="mb-2">
      <div class="search-container">
        <el-input 
          v-model="searchForm.keyword" 
          placeholder="请输入用户名或昵称" 
          class="search-input"
          @keyup.enter="searchUsers"
        >
          <el-button slot="append" type="primary" @click="searchUsers">搜索</el-button>
        </el-input>
      </div>
      <!-- 搜索结果 -->
      <div v-if="searchResults.length > 0" class="search-results">
        <el-divider content-position="left">搜索结果</el-divider>
        <el-row :gutter="20">
          <el-col :span="6" v-for="user in searchResults" :key="user.user_id" class="user-card">
            <el-card>
              <div class="user-info">
                <el-avatar :size="48" class="user-avatar">
                  {{ user.nick_name.charAt(0) }}
                </el-avatar>
                <div class="user-details">
                  <div class="user-nickname">{{ user.nick_name }}</div>
                  <div class="user-username">{{ user.user_name }}</div>
                </div>
              </div>
              <div class="user-actions">
                <el-button type="primary" size="small" @click="sendRequest(user.user_id)">添加好友</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>

    <!-- 好友管理区域 -->
    <el-card>
      <template slot="header">
        <div class="card-header">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="我的好友" name="list"></el-tab-pane>
            <el-tab-pane label="好友申请" name="requests"></el-tab-pane>
          </el-tabs>
        </div>
      </template>

      <!-- 我的好友列表 -->
      <div v-if="activeTab === 'list'">
        <el-row :gutter="20">
          <el-col :span="6" v-for="friend in friendList" :key="friend.user_id" class="friend-card">
            <el-card>
              <div class="friend-info">
                <el-avatar :size="48" class="friend-avatar">
                  {{ friend.nick_name.charAt(0) }}
                </el-avatar>
                <div class="friend-details">
                  <div class="friend-nickname">
                    {{ friend.nick_name }}
                    <span class="online-status" v-if="friend.status === '0'"></span>
                  </div>
                  <div class="friend-username">{{ friend.user_name }}</div>
                </div>
              </div>
              <div class="friend-actions">
                <el-button type="primary" size="small" @click="handleChat(friend.user_id)">聊天</el-button>
                <el-button type="danger" size="small" @click="handleDelete(friend.user_id)">删除</el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
        <el-empty v-if="friendList.length === 0" description="暂无好友" />
      </div>

      <!-- 好友申请列表 -->
      <div v-else-if="activeTab === 'requests'">
        <el-table :data="friendRequests" style="width: 100%">
          <el-table-column label="申请人" width="180">
            <template slot-scope="scope">
              <div class="request-user">
                <el-avatar :size="36" class="request-avatar">
                  {{ scope.row.nick_name.charAt(0) }}
                </el-avatar>
                <div class="request-user-info">
                  <div class="request-nickname">{{ scope.row.nick_name }}</div>
                  <div class="request-username">{{ scope.row.user_name }}</div>
                </div>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="message" label="申请留言" min-width="300"></el-table-column>
          <el-table-column prop="create_time" label="申请时间" width="180"></el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button size="mini" type="success" @click="handleAccept(scope.row.id)">同意</el-button>
              <el-button size="mini" type="danger" @click="handleReject(scope.row.id)">拒绝</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="friendRequests.length === 0" description="暂无好友申请" />
      </div>
    </el-card>

    <!-- 发送申请对话框 -->
    <el-dialog title="发送好友申请" :visible.sync="requestDialogVisible" width="500px">
      <el-form :model="requestForm" label-width="80px">
        <el-form-item label="申请留言">
          <el-input type="textarea" v-model="requestForm.message" placeholder="请输入申请留言" rows="3"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="requestDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRequest">发送</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { searchUsers, sendFriendRequest, getFriendRequests, handleRequest, getFriendList, deleteFriend, getFriendPublicKey } from '@/api/friend'

export default {
  name: 'Friend',
  data() {
    return {
      activeTab: 'list',
      friendList: [],
      friendRequests: [],
      searchDialogVisible: false,
      requestDialogVisible: false,
      searchForm: {
        keyword: ''
      },
      requestForm: {
        message: '请求添加您为好友'
      },
      searchResults: [],
      targetUserId: null
    }
  },
  created() {
    this.getFriendList()
    this.getFriendRequests()
  },
  methods: {
    // 获取好友列表
    getFriendList() {
      getFriendList().then(response => {
        this.friendList = response.data
      })
    },
    // 获取待处理的申请列表
    getFriendRequests() {
      getFriendRequests().then(response => {
        this.friendRequests = response.data
      })
    },
    // 搜索用户
    handleSearchUser() {
      this.searchDialogVisible = true
    },
    searchUsers() {
      if (!this.searchForm.keyword) {
        this.$message.warning('请输入搜索关键词')
        return
      }
      searchUsers(this.searchForm.keyword).then(response => {
        this.searchResults = response.data
      }).catch(error => {
        console.error('搜索用户失败:', error)
        this.$message.error('搜索失败，请重试')
      })
    },
    // 发送好友申请
    sendRequest(userId) {
      this.targetUserId = userId
      this.requestDialogVisible = true
    },
    confirmRequest() {
      sendFriendRequest({
        to_user_id: this.targetUserId,
        message: this.requestForm.message
      }).then(response => {
        this.$message.success('发送成功')
        this.requestDialogVisible = false
        this.requestForm.message = '请求添加您为好友'
      }).catch(error => {
        console.error('发送好友申请失败:', error)
        this.$message.error('发送失败，请重试')
      })
    },
    // 处理申请
    handleAccept(id) {
      handleRequest(id, 1).then(response => {
        this.$message.success('已同意')
        this.getFriendRequests()
        this.getFriendList()
      })
    },
    handleReject(id) {
      handleRequest(id, 2).then(response => {
        this.$message.success('已拒绝')
        this.getFriendRequests()
      })
    },
    // 删除好友
    handleDelete(friendId) {
      this.$confirm('确定要删除该好友吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteFriend(friendId).then(response => {
          this.$message.success('删除成功')
          this.getFriendList()
        })
      })
    },
    // 获取好友公钥
    handleGetPublicKey(friendId) {
      getFriendPublicKey(friendId).then(response => {
        this.$message.success('获取成功')
        console.log('好友公钥:', response.data.public_key)
      })
    },
    // 聊天
    handleChat(friendId) {
      this.$router.push(`/chat/${friendId}`)
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

.mb-2 {
  margin-bottom: 16px;
}

.search-container {
  margin-bottom: 16px;
}

.search-input {
  width: 400px;
}

.search-results {
  margin-top: 16px;
}

.user-card,
.friend-card {
  margin-bottom: 20px;
}

.user-info,
.friend-info {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.user-avatar,
.friend-avatar {
  margin-right: 12px;
}

.user-details,
.friend-details {
  flex: 1;
}

.user-nickname,
.friend-nickname {
  font-weight: bold;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.user-username,
.friend-username {
  font-size: 12px;
  color: #909399;
}

.user-actions,
.friend-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 16px;
}

.online-status {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #67c23a;
  margin-left: 8px;
}

.request-user {
  display: flex;
  align-items: center;
}

.request-avatar {
  margin-right: 12px;
}

.request-user-info {
  flex: 1;
}

.request-nickname {
  font-weight: bold;
  margin-bottom: 4px;
}

.request-username {
  font-size: 12px;
  color: #909399;
}
</style>