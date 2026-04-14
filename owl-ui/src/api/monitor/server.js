import request from '@/utils/request'

// 获取服务信息
export function getServer() {
  return request({
    url: '/monitor/server',
    method: 'get'
  })
}

// 系统监控概览：用户总数、加密文件存储总量
export function getOverview() {
  return request({
    url: '/monitor/overview',
    method: 'get'
  })
}
