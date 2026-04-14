<template>
  <div class="friend-list">
    <el-input v-model="searchText" placeholder="搜索好友" class="search-input"></el-input>
    <div class="friend-list-container">
      <div
        v-for="friend in filteredFriends"
        :key="friend.user_id"
        class="friend-item"
        :class="{ active: activeFriendId === friend.user_id }"
        @click="selectFriend(friend)"
      >
        <div class="friend-item-content">
          <div class="friend-avatar">
            <el-avatar :size="48">
              {{ friend.nick_name.charAt(0) }}
            </el-avatar>
            <span class="online-status" v-if="friend.online"></span>
          </div>
          <div class="friend-info">
            <div class="friend-name">{{ friend.nick_name }}</div>
            <div class="friend-last-msg">{{ friend.last_msg_content || '暂无消息' }}</div>
          </div>
          <div class="friend-meta">
            <div class="friend-time" v-if="friend.last_msg_time">{{ formatTime(friend.last_msg_time) }}</div>
            <el-badge v-if="friend.unread_count > 0" :value="friend.unread_count" type="danger" />
          </div>
        </div>
      </div>
    </div>
    <div class="empty-state" v-if="filteredFriends.length === 0">
      <el-empty description="暂无好友" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'FriendList',
  props: {
    friends: {
      type: Array,
      default: () => []
    },
    activeFriendId: {
      type: Number,
      default: null
    }
  },
  data() {
    return {
      searchText: ''
    }
  },
  computed: {
    filteredFriends() {
      if (!this.searchText) {
        return this.friends
      }
      const searchLower = this.searchText.toLowerCase()
      return this.friends.filter(friend => 
        friend.nick_name.toLowerCase().includes(searchLower) ||
        friend.user_name.toLowerCase().includes(searchLower)
      )
    }
  },
  methods: {
    selectFriend(friend) {
      this.$emit('select', friend)
    },
    formatTime(time) {
      if (!time) return ''
      const date = new Date(time)
      return date.toLocaleString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.friend-list {
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #e4e7ed;
}

.search-input {
  margin: 10px;
  width: calc(100% - 20px);
}

.friend-list-container {
  flex: 1;
  overflow-y: auto;
}

.friend-item {
  cursor: pointer;
  transition: all 0.3s;
  padding: 10px;
  position: relative;
}

.friend-item:hover {
  background-color: #f5f7fa;
}

.friend-item.active {
  background-color: #ecf5ff;
}

.friend-item-content {
  display: flex;
  align-items: center;
}

.friend-avatar {
  position: relative;
  margin-right: 10px;
}

.online-status {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #67c23a;
  border: 2px solid white;
}

.friend-info {
  flex: 1;
  overflow: hidden;
}

.friend-name {
  font-weight: bold;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.friend-last-msg {
  font-size: 12px;
  color: #909399;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.friend-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.friend-time {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.empty-state {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>