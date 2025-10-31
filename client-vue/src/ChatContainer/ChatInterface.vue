<template>
  <div class="chat-container">
    <!-- Chat message area using new MessageBubble system -->
    <ChatContainer
      ref="chatContainer"
      class="chat-area"
      :messages="formattedMessages"
      :auto-scroll="true"
      :current-user-id="currentUserId"
      @message-edit="handleMessageEdit"
      @message-delete="handleMessageDelete"
      @message-copy="handleMessageCopy"
      @messages-change="handleMessagesChange"
    />

    <!-- Input area -->
    <div class="input-area">
      <div class="input-header">
        <select v-model="messageType" class="type-selector">
          <option value="text">Text</option>
          <option value="markdown">Markdown</option>
        </select>
        <div class="input-hint">
          Ctrl+Enter 发送 • 支持 Markdown 格式
        </div>
      </div>
      <div class="input-row">
        <textarea
          v-model="inputMessage"
          @keydown.ctrl.enter="sendMessage"
          placeholder="输入您的消息... (Ctrl+Enter 快速发送)"
          class="message-input"
          rows="2"
        ></textarea>
        <button
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
          class="send-button"
        >
          <span class="send-icon">➤</span>
          发送
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { GetSpecificMessages } from '../idb'
import ChatContainer from './ChatContainer.vue'
import type { MessageData } from './MessageBubble.vue'

interface ExtendedMessageData extends MessageData {
  editable?: boolean
  showButtons?: boolean
}

interface DbMessage {
  id?: string
  content: string
  sender?: string
  timestamp?: Date | number
  type?: string
}

// Reactive data
const chatContainer = ref<InstanceType<typeof ChatContainer>>()
const inputMessage = ref('')
const messageType = ref<'text' | 'markdown'>('markdown')
const messages = ref<DbMessage[]>([])
const currentUserId = 'current-user'

// Generate unique ID
const generateId = () => Date.now().toString() + Math.random().toString(36).substr(2, 9)

// Convert database messages to our format
const formattedMessages = computed((): ExtendedMessageData[] => {
  return messages.value.map((msg, index) => ({
    id: msg.id || `msg-${index}`,
    sender: msg.sender || 'user',
    content: msg.content,
    timestamp: msg.timestamp || new Date(),
    type: msg.type || 'text',
    editable: true,
    showButtons: true
  }))
})

// Send message
const sendMessage = () => {
  if (!inputMessage.value.trim()) return

  const message: ExtendedMessageData = {
    id: generateId(),
    sender: currentUserId,
    content: inputMessage.value.trim(),
    timestamp: new Date(),
    type: messageType.value,
    editable: true,
    showButtons: true
  }

  if (chatContainer.value) {
    chatContainer.value.addMessage(message)
  }

  inputMessage.value = ''
}

// Event handlers
const handleMessageEdit = (messageId: string, content: string) => {
  console.log('Edit message:', messageId, content)
  const newContent = prompt('Edit message:', content)
  if (newContent !== null && chatContainer.value) {
    chatContainer.value.updateMessage(messageId, { content: newContent })
  }
}

const handleMessageDelete = (messageId: string) => {
  console.log('Delete message:', messageId)
}

const handleMessageCopy = (content: string) => {
  console.log('Copy message:', content)
}

const handleMessagesChange = (messages: ExtendedMessageData[]) => {
  console.log('Messages changed:', messages.length, 'messages')
}

// Fetch messages from database when component is mounted
onMounted(async () => {
  try {
    const { message } = await GetSpecificMessages('GaMessages')
    messages.value = message || []
    console.log('Messages loaded:', messages.value)

    // If there are no messages, add a welcome message
    if (messages.value.length === 0) {
      setTimeout(() => {
        const welcomeMessage: ExtendedMessageData = {
          id: generateId(),
          sender: 'system',
          content: '# 欢迎使用 Markdown 聊天! 🎉\\n\\n此聊天支持 **Markdown 格式化**：\\n- **粗体文本**\\n- *斜体文本*\\n- `代码片段`\\n- 以及更多功能!\\n\\n请在下方输入消息开始聊天!',
          timestamp: new Date(),
          type: 'markdown',
          editable: false,
          showButtons: false
        }

        if (chatContainer.value) {
          chatContainer.value.addMessage(welcomeMessage)
        }
      }, 500)
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

/* ChatContainer容器 - 限制宽度与输入区域一致 */
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  background: #667eea;
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
  color: rgba(102, 126, 234, 0.6);
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
  min-width: 60px;
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
  font-size: 10px;
  transform: rotate(0deg);
  transition: transform 0.2s ease;
}

.send-button:hover:not(:disabled) .send-icon {
  transform: rotate(15deg);
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
