import request from '@/utils/request'
import { saveAs } from 'file-saver'
import { blobValidate } from '@/utils/ruoyi'
import errorCode from '@/utils/errorCode'

// 个人中心使用统计：文件数量、存储空间（字节）
export function getFileStats() {
  return request({
    url: '/encry/file/stats',
    method: 'get'
  })
}

// 查询加密文件列表
export function listFile(query) {
  return request({
    url: '/encry/file/list',
    method: 'get',
    params: query
  })
}

// 加密上传文件
export function uploadFile(file, encryptAlgo = 'AES') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('encryptAlgo', encryptAlgo)
  return request({
    url: '/encry/file/upload',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取文件哈希值
export function getFileHash(fileId) {
  return request({
    url: '/encry/file/hash/' + fileId,
    method: 'get'
  })
}

// 解密下载文件，verifyHash 可选，用于完整性校验
export function downloadFile(fileId, filename, verifyHash) {
  const params = verifyHash ? { verifyHash } : {}
  return request({
    url: '/encry/file/download/' + fileId,
    method: 'get',
    params,
    responseType: 'blob'
  }).then(async res => {
    // request 拦截器对 blob 请求直接返回 res.data，故 res 即为 blob 本身
    const blob = res instanceof Blob ? res : res.data
    const isBlob = await blobValidate(blob)
    if (isBlob) {
      saveAs(blob, filename || 'download')
      return
    }
    // 响应实为 JSON 错误（如 500 被网关改为 2xx 或后端返回错误体）
    const text = await blob.text()
    let msg = errorCode['default']
    try {
      const rsp = JSON.parse(text)
      msg = rsp.msg || errorCode[rsp.code] || msg
    } catch (e) {
      if (text) msg = text
    }
    return Promise.reject(new Error(msg))
  })
}

// 删除加密文件
export function delFile(fileId) {
  return request({
    url: '/encry/file/' + fileId,
    method: 'delete'
  })
}

// 批量删除加密文件
export function delFiles(fileIds) {
  return request({
    url: '/encry/file/remove/' + (Array.isArray(fileIds) ? fileIds.join(',') : fileIds),
    method: 'delete'
  })
}
