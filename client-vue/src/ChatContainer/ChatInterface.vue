<template>
  <div class="chat-container">
    <!-- 表白墙消息区域 -->
    <ChatContainer
      ref="chatContainer"
      class="chat-area"
      :messages="formattedMessages"
      :auto-scroll="true"
      :current-user-id="currentUserId"
      @message-like="handleMessageLike"
      @message-delete="handleMessageDelete"
      @messages-change="handleMessagesChange"
    />

    <!-- 发布新消息区域 -->
    <div class="input-area">
      <div class="input-header">
        <select v-model="messageType" class="type-selector">
          <option value="text">文本</option>
          <option value="markdown">Markdown</option>
        </select>
        <div class="input-hint">
          支持 Markdown 格式和数学公式
        </div>
      </div>
      <div class="input-row">
        <textarea
          v-model="inputMessage"
          @keydown.ctrl.enter="sendMessage"
          placeholder="写下你的表白或想法... (Ctrl+Enter 快速发布)"
          class="message-input"
          rows="3"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim() || sending"
          class="send-button"
        >
          <span v-if="sending" class="loading-spinner">⏳</span>
          <span v-else class="send-icon">💌</span>
          {{ sending ? '发送中' : '表白' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ChatContainer from './ChatContainer.vue'
import type { MessageData } from './MessageBubble.vue'
import api from '../utils/api'
import { decodeMessagesFromProtobuf, transformProtobufMessages } from '../utils/protobuf'

interface ExtendedMessageData extends MessageData {
  editable?: boolean
  showButtons?: boolean
  likes?: number
  liked?: boolean
  db_id?: number
  user_id?: number
}

interface DbMessage {
  id?: string
  content: string
  sender?: string
  timestamp?: Date | number
  type?: string
  likes?: number
  liked?: boolean
  db_id?: number
  user_id?: number
}

// Reactive data
const chatContainer = ref<InstanceType<typeof ChatContainer>>()
const inputMessage = ref('')
const messageType = ref<'text' | 'markdown'>('markdown')
const messages = ref<DbMessage[]>([])
const currentUserId = 'current-user'
const loading = ref(false)
const sending = ref(false)

// Generate unique ID
const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9)

// Convert database messages to our format and sort by timestamp (newest first)
const formattedMessages = computed((): ExtendedMessageData[] => {
  return messages.value
    .map((msg, index) => ({
      id: msg.id || `msg-${index}`,
      sender: msg.sender || 'user',
      content: msg.content,
      timestamp: msg.timestamp || new Date(),
      type: msg.type || 'text',
      likes: msg.likes || 0,
      liked: msg.liked || false,
      editable: true,
      showButtons: true,
      db_id: msg.db_id,
      user_id: msg.user_id
    }))
    .sort((a, b) => {
      // 按时间倒序排列，最新的在上面
      const timeA = typeof a.timestamp === 'number' ? a.timestamp : new Date(a.timestamp).getTime()
      const timeB = typeof b.timestamp === 'number' ? b.timestamp : new Date(b.timestamp).getTime()
      return timeB - timeA
    })
})

// 从后端获取protobuf消息
const loadMessagesFromProtobuf = async () => {
  try {
    loading.value = true
    console.log('开始从后端获取protobuf消息...')

    const response = await api.post('/api/messages/', {
      limit: 1000
    })

    console.log('获取到消息数据:', response.data)

    // 更新消息列表
    messages.value = response.data.messages.map((msg: any) => ({
      id: msg.message_id,
      content: msg.content,
      sender: msg.username,
      timestamp: msg.timestamp,
      type: msg.type,
      likes: msg.likes,
      liked: msg.liked,
      db_id: msg.db_id,
      user_id: msg.user_id
    }))

    console.log(`成功加载 ${messages.value.length} 条消息`)

  } catch (error) {
    console.error('获取消息失败:', error)

    // 如果获取失败，设置为空数组
    messages.value = []

    // 显示欢迎消息
    setTimeout(() => {
      const welcomeMessage: ExtendedMessageData = {
        id: generateId(),
        sender: 'system',
        content: '# 欢迎来到表白墙! 💌\n\n这里可以：\n- 写下你的表白或想法\n- 使用 **Markdown** 格式\n- 添加数学公式 $$E=mc^2$$\n- 表情符号 :smile: 和上标下标\n\n点赞 ❤️ 你喜欢的表白，删除不需要的内容。\n\n开始你的第一次表白吧!',
        timestamp: new Date(),
        type: 'markdown',
        likes: 0,
        liked: false,
        editable: false,
        showButtons: false
      }

      if (chatContainer.value) {
        chatContainer.value.addMessage(welcomeMessage)
      }

      // 同时添加到本地消息列表
      messages.value.unshift({
        id: welcomeMessage.id,
        content: welcomeMessage.content,
        sender: welcomeMessage.sender,
        timestamp: welcomeMessage.timestamp,
        type: welcomeMessage.type,
        likes: welcomeMessage.likes,
        liked: welcomeMessage.liked
      })
    }, 500)
  } finally {
    loading.value = false
  }
}

// Send message - 使用新的后端接口
const sendMessage = async () => {
  if (!inputMessage.value.trim() || sending.value) return

  // 检查是否有登录状态
  const token = sessionStorage.getItem('token')
  if (!token) {
    console.error('未登录，请先登录')
    alert('请先登录后再发送消息')
    return
  }

  const messageContent = inputMessage.value.trim()
  inputMessage.value = ''
  sending.value = true

  try {
    // 调用新的后端接口发送消息
    const response = await api.post('/api/messages/send', {
      content: messageContent,
      message_type: messageType.value
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    console.log('消息发送成功:', response.data)

    if (response.data.success) {
      // 成功后重新加载消息列表
      await loadMessagesFromProtobuf()
      console.log('消息列表已刷新')
    } else {
      throw new Error(response.data.error || '发送失败')
    }
  } catch (error: any) {
    console.error('发送消息失败:', error)
    const errorMessage = error.response?.data?.detail?.message || error.message || '发送失败'
    alert(`发送消息失败: ${errorMessage}`)

    // 恢复输入框内容
    inputMessage.value = messageContent
  } finally {
    sending.value = false
  }
}

// Event handlers
const handleMessageLike = (messageId: string) => {
  console.log('Like message:', messageId)

  // 更新本地消息状态
  const messageIndex = messages.value.findIndex(m => m.id === messageId)
  if (messageIndex !== -1) {
    const msg = messages.value[messageIndex]
    const isLiked = msg.liked || false
    msg.liked = !isLiked
    msg.likes = (msg.likes || 0) + (isLiked ? -1 : 1)
  }

  // 更新ChatContainer中的消息
  if (chatContainer.value) {
    const message = chatContainer.value.getMessageById(messageId)
    if (message) {
      const isLiked = message.liked || false
      chatContainer.value.updateMessage(messageId, {
        liked: !isLiked,
        likes: (message.likes || 0) + (isLiked ? -1 : 1)
      })
    }
  }
}

const handleMessageDelete = (messageId: string) => {
  console.log('Delete message:', messageId)

  // 从本地消息列表中移除
  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    messages.value.splice(index, 1)
  }

  // 从ChatContainer中移除
  if (chatContainer.value) {
    chatContainer.value.removeMessage(messageId)
  }
}

const handleMessagesChange = (messages: ExtendedMessageData[]) => {
  console.log('Messages changed:', messages.length, 'messages')
}

// Fetch messages from backend when component is mounted
onMounted(async () => {
  try {
    // 首先尝试从后端获取消息
    await loadMessagesFromProtobuf()

    // 如果没有获取到消息，onMounted已经处理了
    if (messages.value.length === 0) {
      console.log('未获取到消息，显示欢迎消息')
    }
  } catch (error) {
    console.error('Error loading messages:', error)
  }
})
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100dvh - 60px);
  max-width: 900px;
  margin: 0 auto;
  background: #f8fafc;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

/* ChatContainer容器 */
.chat-area {
  flex: 1;
  position: relative;
  min-height: 0;
  background: transparent;
  margin: 0;
  overflow: hidden;
}

/* 输入区域样式 */
.input-area {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
  padding: 12px 16px;
  margin: 0 16px 16px 16px;
  border-radius: 0 0 12px 12px;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
}

.input-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.type-selector {
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  padding: 4px 8px;
  color: white;
  font-size: 12px;
  font-weight: 500;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.type-selector:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.3);
}

.type-selector:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
}

.type-selector option {
  background: #ff6b6b;
  color: white;
}

.input-hint {
  color: rgba(255, 255, 255, 0.8);
  font-size: 10px;
  font-weight: 400;
}

.input-row {
  display: flex;
  gap: 8px;
  align-items: flex-end;
}

.message-input {
  flex: 1;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  line-height: 1.4;
  color: #333;
  resize: vertical;
  min-height: 40px;
  max-height: 80px;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.message-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 1);
  border-color: rgba(255, 255, 255, 0.5);
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.2), 0 2px 8px rgba(0, 0, 0, 0.1);
}

.message-input::placeholder {
  color: rgba(255, 107, 107, 0.6);
  font-style: italic;
}

.send-button {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  padding: 8px 16px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
  min-width: 70px;
  justify-content: center;
}

.send-button:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.send-button:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: rgba(255, 255, 255, 0.1);
}

.send-icon {
  font-size: 12px;
  transform: rotate(0deg);
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-icon {
  transform: rotate(15deg);
}

.loading-spinner {
  font-size: 12px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    margin: 8px;
    border-radius: 8px;
    height: calc(100dvh - 40px);
  }

  .input-area {
    margin: 0 12px 12px 12px;
    padding: 10px 12px;
    border-radius: 0 0 8px 8px;
  }

  .input-header {
    flex-direction: column;
    gap: 6px;
    align-items: flex-start;
  }

  .input-row {
    flex-direction: column;
    gap: 8px;
  }

  .send-button {
    width: 100%;
    padding: 12px 16px;
  }
}

/* 滚动条样式 */
.message-input::-webkit-scrollbar {
  width: 6px;
}

.message-input::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.message-input::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.message-input::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>
