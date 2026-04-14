import request from '@/utils/request'

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
export function downloadShare(shareId) {
  return request({
    url: `/encry/file/share/download/${shareId}`,
    method: 'get',
    responseType: 'blob'
  }).then(response => {
    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    
    // 从响应头中获取文件名
    const contentDisposition = response.headers['content-disposition']
    let fileName = 'download'
    if (contentDisposition) {
      const match = contentDisposition.match(/filename="(.*)"/)
      if (match && match[1]) {
        fileName = match[1]
      }
    }
    
    a.download = fileName
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
  })
}
