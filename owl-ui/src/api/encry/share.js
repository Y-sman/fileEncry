import request from '@/utils/request'
import { saveAs } from 'file-saver'
import { blobValidate } from '@/utils/ruoyi'
import errorCode from '@/utils/errorCode'

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

export function getSharedToMe(params) {
  return request({
    url: '/encry/file/shared-to-me',
    method: 'get',
    params
  })
}

export function getSharedByMe(params) {
  return request({
    url: '/encry/file/shared-by-me',
    method: 'get',
    params
  })
}

export function revokeShare(shareId) {
  return request({
    url: `/encry/file/share/${shareId}`,
    method: 'delete'
  })
}

async function saveShareBlob(blob, filename) {
  const isBlob = await blobValidate(blob)
  if (isBlob) {
    saveAs(blob, filename || 'download')
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
  throw new Error(msg)
}

export function downloadShare(shareId, filename) {
  return request({
    url: `/encry/file/share/download/${shareId}`,
    method: 'get',
    responseType: 'blob'
  }).then(blob => saveShareBlob(blob, filename))
}

export function downloadShareByFile(fileId, filename) {
  return request({
    url: `/encry/file/share/download/by-file/${fileId}`,
    method: 'get',
    responseType: 'blob'
  }).then(blob => saveShareBlob(blob, filename))
}
