import request from '@/utils/request'
import { saveAs } from 'file-saver'
import { blobValidate } from '@/utils/ruoyi'
import errorCode from '@/utils/errorCode'

// 分享文件
export function shareFile(fileId, targetUserId) {
  return request({
    url: '/encry/file/share',
    method: 'post',
    data: {
      file_id: fileId,
      target_user_id: targetUserId
    }
  })
}

// 分享给我的文件列表
export function getSharedToMe(params) {
  return request({
    url: '/encry/file/shared-to-me',
    method: 'get',
    params
  })
}

// 我分享的文件列表
export function getSharedByMe(params) {
  return request({
    url: '/encry/file/shared-by-me',
    method: 'get',
    params
  })
}

// 撤销分享
export function revokeShare(shareId) {
  return request({
    url: `/encry/file/share/${shareId}`,
    method: 'delete'
  })
}

// 下载分享的文件
export function downloadShare(shareId, filename) {
  return request({
    url: `/encry/file/share/download/${shareId}`,
    method: 'get',
    responseType: 'blob'
  }).then(async res => {
    const blob = res instanceof Blob ? res : res.data
    const isBlob = await blobValidate(blob)
    if (isBlob) {
      saveAs(blob, filename || 'shared-file.bin')
      return
    }
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
