<template>
  <div class="chat-container">
    <!-- Chat message area using new MessageBubble system -->
    <ChatContainer
      ref="chatContainer"
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
      <div class="input-controls">
        <select v-model="messageType" class="type-selector">
          <option value="text">Text</option>
          <option value="markdown">Markdown</option>
        </select>
      </div>
      <div class="input-row">
        <textarea
          v-model="inputMessage"
          @keydown.ctrl.enter="sendMessage"
          placeholder="Type your message... (Ctrl+Enter to send, supports Markdown)"
          class="message-input"
          rows="3"
        ></textarea>
        <button @click="sendMessage" :disabled="!inputMessage.trim()" class="send-button">
          Send
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

const handleMessagesChange = (newMessages: ExtendedMessageData[]) => {
  console.log('Messages changed:', newMessages.length, 'messages')
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
          content: '# Welcome to Markdown Chat! 🎉\n\nThis chat supports **markdown formatting**:\n- **Bold text**\n- *Italic text*\n- `code snippets`\n- And much more!\n\nTry typing a message below!',
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
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  border: 1px solid #ccc;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 15px;
  resize: vertical;
  min-height: 300px;
  max-height: 600px;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 10px;
  padding: 8px 12px;
  background-color: #e3f2fd;
  border-radius: 12px;
  max-width: 80%;
}

.message-content {
  word-wrap: break-word;
}

.input-area {
  display: flex;
  gap: 10px;
}

.message-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.send-button {
  padding: 12px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.send-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}
</style>
