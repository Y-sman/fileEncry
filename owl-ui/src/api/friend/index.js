import request from '@/utils/request'

// 搜索用户
export function searchUsers(keyword) {
  return request({
    url: '/friend/search',
    method: 'get',
    params: { keyword }
  })
}

// 发送好友申请
export function sendFriendRequest(data) {
  return request({
    url: '/friend/request',
    method: 'post',
    data
  })
}

// 获取待处理的申请列表
export function getFriendRequests() {
  return request({
    url: '/friend/requests',
    method: 'get'
  })
}

// 处理申请
export function handleRequest(id, status) {
  return request({
    url: '/friend/request/' + id,
    method: 'put',
    data: { status }
  })
}

// 获取好友列表
export function getFriendList() {
  return request({
    url: '/friend/list',
    method: 'get'
  })
}

// 删除好友
export function deleteFriend(friendId) {
  return request({
    url: '/friend/' + friendId,
    method: 'delete'
  })
}

// 获取好友公钥
export function getFriendPublicKey(friendId) {
  return request({
    url: '/friend/public-key/' + friendId,
    method: 'get'
  })
}
