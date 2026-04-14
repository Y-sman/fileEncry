import request from '@/utils/request'

// 获取用户公钥
export function getUserPublicKey(userId) {
  return request({
    url: `/encry/key/public/${userId}`,
    method: 'get'
  })
}

// 为分享而加密上传文件
export function uploadEncryptedFile(file, receiverId) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('receiver_id', receiverId)
  return request({
    url: '/encry/file/share/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取密钥信息
export function getKeyInfo() {
  return request({
    url: '/encry/key/info',
    method: 'get'
  })
}

// 生成密钥
export function generateKey(keySize) {
  return request({
    url: '/encry/key/generate',
    method: 'post',
    data: { keySize }
  })
}

// 导出公钥
export function exportPublicKey() {
  return request({
    url: '/encry/key/export/public',
    method: 'get'
  })
}

// 导出私钥
export function exportPrivateKey() {
  return request({
    url: '/encry/key/export/private',
    method: 'get'
  })
}
