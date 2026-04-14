import request from '@/utils/request'

// 获取历史消息
export function getHistory(friendId, page, pageSize) {
  return request({
    url: '/chat/history/' + friendId,
    method: 'get',
    params: { page, pageSize }
  })
}

// 获取最近会话列表
export function getSessions() {
  return request({
    url: '/chat/sessions',
    method: 'get'
  })
}

// 标记与某好友的消息为已读
export function markAsRead(friendId) {
  return request({
    url: '/chat/read/' + friendId,
    method: 'put'
  })
}
