<template>
  <div class="chat-container">
    <div class="chat-messages" ref="messagesContainer">
      <MessageBubble
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :variant="getMessageVariant(message)"
        :editable="message.editable !== false"
        :show-buttons="message.showButtons !== false"
        @edit="handleEdit"
        @copy="handleCopy"
        @delete="handleDelete"
      >
        <!-- Custom buttons slot -->
        <template #buttons v-if="message.customButtons">
          <button
            v-for="button in message.customButtons"
            :key="button.id"
            @click="button.onClick(message.id)"
            class="action-button custom-button"
            :class="button.class"
          >
            {{ button.label }}
          </button>
        </template>
      </MessageBubble>
    </div>

    <!-- Scroll to bottom button -->
    <button
      v-if="showScrollButton"
      @click="() => scrollToBottom()"
      class="scroll-to-bottom"
      title="Scroll to bottom"
    >
      ↓
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import MessageBubble, { type MessageData } from './MessageBubble.vue'

interface CustomButton {
  id: string
  label: string
  onClick: (messageId: string) => void
  class?: string
}

interface ExtendedMessageData extends MessageData {
  editable?: boolean
  showButtons?: boolean
  customButtons?: CustomButton[]
}

interface Props {
  messages?: ExtendedMessageData[]
  autoScroll?: boolean
  currentUserId?: string
}

const props = withDefaults(defineProps<Props>(), {
  messages: () => [],
  autoScroll: true,
  currentUserId: 'current-user'
})

const emit = defineEmits<{
  messageEdit: [messageId: string, content: string]
  messageDelete: [messageId: string]
  messageCopy: [content: string]
  messagesChange: [messages: ExtendedMessageData[]]
}>()

// Reactive data
const messagesContainer = ref<HTMLElement>()
const showScrollButton = ref(false)
const messages = ref<ExtendedMessageData[]>([...props.messages])

// Watch for prop changes
watch(() => props.messages, (newMessages) => {
  messages.value = [...newMessages]
  if (props.autoScroll) {
    nextTick(() => scrollToBottom())
  }
}, { deep: true })

// Monitor scroll position
const handleScroll = () => {
  if (!messagesContainer.value) return

  const { scrollTop, scrollHeight, clientHeight } = messagesContainer.value
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
  showScrollButton.value = !isNearBottom
}

// Scroll to bottom
const scrollToBottom = (smooth = true) => {
  if (!messagesContainer.value) return

  messagesContainer.value.scrollTo({
    top: messagesContainer.value.scrollHeight,
    behavior: smooth ? 'smooth' : 'auto'
  })
}

// Get message variant based on sender
const getMessageVariant = (message: ExtendedMessageData): 'sent' | 'received' | 'system' => {
  if (message.sender === 'system') return 'system'
  if (message.sender === props.currentUserId) return 'sent'
  return 'received'
}

// Event handlers
const handleEdit = (messageId: string) => {
  const message = messages.value.find(m => m.id === messageId)
  if (message) {
    emit('messageEdit', messageId, message.content)
  }
}

const handleCopy = async (content: string) => {
  try {
    await navigator.clipboard.writeText(content)
    emit('messageCopy', content)
  } catch (err) {
    console.error('Failed to copy text: ', err)
  }
}

const handleDelete = (messageId: string) => {
  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    messages.value.splice(index, 1)
    emit('messageDelete', messageId)
    emit('messagesChange', messages.value)
  }
}

// Public methods for dynamic editing
const addMessage = (message: ExtendedMessageData) => {
  messages.value.push(message)
  emit('messagesChange', messages.value)

  if (props.autoScroll) {
    nextTick(() => scrollToBottom())
  }
}

const updateMessage = (messageId: string, updates: Partial<ExtendedMessageData>) => {
  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    messages.value[index] = { ...messages.value[index], ...updates }
    emit('messagesChange', messages.value)
  }
}

const removeMessage = (messageId: string) => {
  const index = messages.value.findIndex(m => m.id === messageId)
  if (index !== -1) {
    messages.value.splice(index, 1)
    emit('messagesChange', messages.value)
  }
}

const clearMessages = () => {
  messages.value = []
  emit('messagesChange', messages.value)
}

const insertMessage = (index: number, message: ExtendedMessageData) => {
  messages.value.splice(index, 0, message)
  emit('messagesChange', messages.value)
}

const getMessages = (): ExtendedMessageData[] => {
  return [...messages.value]
}

const getMessageById = (messageId: string): ExtendedMessageData | undefined => {
  return messages.value.find(m => m.id === messageId)
}

// Expose methods to parent component
defineExpose({
  addMessage,
  updateMessage,
  removeMessage,
  clearMessages,
  insertMessage,
  getMessages,
  getMessageById,
  scrollToBottom
})

onMounted(() => {
  if (messagesContainer.value) {
    messagesContainer.value.addEventListener('scroll', handleScroll)

    // Scroll to bottom initially if autoScroll is enabled
    if (props.autoScroll && messages.value.length > 0) {
      nextTick(() => scrollToBottom(false))
    }
  }
})
</script>

<style scoped>
.chat-container {
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  scroll-behavior: smooth;
}

/* Custom scrollbar */
.chat-messages::-webkit-scrollbar {
  width: 8px;
}

.chat-messages::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Scroll to bottom button */
.scroll-to-bottom {
  position: absolute;
  bottom: 20px;
  right: 20px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  font-size: 18px;
  z-index: 10;
}

.scroll-to-bottom:hover {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.scroll-to-bottom:active {
  transform: translateY(0);
}

/* Custom button styles */
.custom-button {
  /* Inherits base styles from MessageBubble component */
}

/* Responsive design */
@media (max-width: 768px) {
  .chat-messages {
    padding: 12px;
  }

  .scroll-to-bottom {
    width: 36px;
    height: 36px;
    font-size: 16px;
    bottom: 16px;
    right: 16px;
  }
}
</style>
