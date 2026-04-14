import io from 'socket.io-client'
import { getToken } from '@/utils/auth'

class SocketClient {
  constructor() {
    this.socket = null
    this.isConnected = false
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000 // 1秒
    this.callbacks = {
      message: [],
      friendOnline: [],
      friendOffline: []
    }
  }

  /**
   * 建立 WebSocket 连接
   * @returns {Promise}
   */
  connect() {
    return new Promise((resolve, reject) => {
      // 如果已经连接，直接返回
      if (this.isConnected) {
        resolve(this.socket)
        return
      }

      // 获取 token
      const token = getToken()
      if (!token) {
        reject(new Error('未登录，无法建立 WebSocket 连接'))
        return
      }

      // 创建 socket 连接 - 直接连接到后端 9000 端口
      this.socket = io('http://localhost:9000', {
        path: '/socket.io',
        transports: ['websocket', 'polling'],
        query: {
          token
        },
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
        timeout: 20000 // 20秒超时
      })

      // 连接成功
      this.socket.on('connect', () => {
        console.log('WebSocket 连接成功')
        this.isConnected = true
        this.reconnectAttempts = 0
        resolve(this.socket)
      })

      // 连接失败
      this.socket.on('connect_error', (error) => {
        console.error('WebSocket 连接失败:', error)
        console.error('错误详情:', error.message, error.code, error.stack)
        this.isConnected = false
        reject(error)
      })

      // 连接超时
      this.socket.on('connect_timeout', (timeout) => {
        console.error('WebSocket 连接超时:', timeout)
        this.isConnected = false
      })

      // 重连尝试
      this.socket.on('reconnect_attempt', (attemptNumber) => {
        console.log(`WebSocket 尝试重连 (${attemptNumber})...`)
      })

      // 重连失败
      this.socket.on('reconnect_failed', () => {
        console.error('WebSocket 重连失败')
        this.isConnected = false
      })

      // 重连成功
      this.socket.on('reconnect', (attemptNumber) => {
        console.log(`WebSocket 重连成功 (${attemptNumber})`)
        this.isConnected = true
        this.reconnectAttempts = 0
      })

      // 断开连接
      this.socket.on('disconnect', (reason) => {
        console.log('WebSocket 断开连接:', reason)
        this.isConnected = false
        // 自动重连
        this.autoReconnect()
      })

      // 接收消息（来自其他用户）
      this.socket.on('chat.message', (data) => {
        console.log('收到消息(chat.message):', data)
        this.callbacks.message.forEach(callback => {
          callback(data)
        })
      })

      // 接收消息确认（自己发送的消息回执）
      this.socket.on('chat.message.sent', (data) => {
        console.log('消息发送确认(chat.message.sent):', data)
        this.callbacks.message.forEach(callback => {
          callback(data)
        })
      })

      // 好友上线
      this.socket.on('user.online', (data) => {
        console.log('好友上线:', data)
        this.callbacks.friendOnline.forEach(callback => {
          callback(data)
        })
      })

      // 好友下线
      this.socket.on('user.offline', (data) => {
        console.log('好友下线:', data)
        this.callbacks.friendOffline.forEach(callback => {
          callback(data)
        })
      })

      // 错误
      this.socket.on('error', (error) => {
        console.error('WebSocket 错误:', error)
      })
    })
  }

  /**
   * 自动重连
   */
  autoReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`WebSocket 尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      setTimeout(() => {
        this.connect().catch(error => {
          console.error('WebSocket 重连失败:', error)
        })
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('WebSocket 重连失败，已达到最大尝试次数')
    }
  }

  /**
   * 发送消息
   * @param {number} receiverId - 接收者 ID
   * @param {string} content - 消息内容
   * @param {number} msgType - 消息类型，默认 1（文本）
   * @returns {Promise}
   */
  sendMessage(receiverId, content, msgType = 1) {
    return new Promise((resolve, reject) => {
      if (!this.isConnected || !this.socket) {
        reject(new Error('WebSocket 未连接'))
        return
      }

      this.socket.emit('chat.message', {
        receiver_id: receiverId,
        content,
        msg_type: msgType
      }, (response) => {
        if (response && response.error) {
          reject(new Error(response.error))
        } else {
          resolve(response)
        }
      })
    })
  }

  /**
   * 监听接收消息
   * @param {Function} callback - 回调函数
   */
  onReceiveMessage(callback) {
    if (typeof callback === 'function') {
      this.callbacks.message.push(callback)
    }
  }

  /**
   * 监听好友上线
   * @param {Function} callback - 回调函数
   */
  onFriendOnline(callback) {
    if (typeof callback === 'function') {
      this.callbacks.friendOnline.push(callback)
    }
  }

  /**
   * 监听好友下线
   * @param {Function} callback - 回调函数
   */
  onFriendOffline(callback) {
    if (typeof callback === 'function') {
      this.callbacks.friendOffline.push(callback)
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.isConnected = false
      this.reconnectAttempts = 0
      console.log('WebSocket 连接已断开')
    }
  }

  /**
   * 获取连接状态
   * @returns {boolean}
   */
  getConnectionStatus() {
    return this.isConnected
  }
}

// 导出单例
const socketClient = new SocketClient()
export default socketClient