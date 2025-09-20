<template>
  <div class="chat-container">
    <RecycleScroller
      class="chat-messages"
      :items="messages"
      :item-size="160"
      size-field="height"
      key-field="id"
      item-class="message-wrapper"
      v-slot="{ item }"
      ref="scroller"
      @scroll="handleScroll"
    >
      <MessageBubble
        :message="item"
        :variant="getMessageVariant(item)"
        :editable="item.editable !== false"
        :show-buttons="item.showButtons !== false"
        @edit="handleEdit"
        @copy="handleCopy"
        @delete="handleDelete"
      >
        <template #buttons v-if="item.customButtons">
          <button
            v-for="button in item.customButtons"
            :key="button.id"
            @click="button.onClick(item.id)"
            class="action-button custom-button"
            :class="button.class"
          >
            {{ button.label }}
          </button>
        </template>
      </MessageBubble>
    </RecycleScroller>

    <button
      v-if="showScrollButton"
      @click="scrollToBottom"
      class="scroll-to-bottom"
      title="滚动到底部"
    >
      ⬇
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, watch, onMounted } from 'vue'
import MessageBubble, { type MessageData } from './MessageBubble.vue'
import { RecycleScroller } from 'vue-virtual-scroller'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

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
const scroller = ref()
const showScrollButton = ref(false)
const messages = ref<ExtendedMessageData[]>([...props.messages])

// Watch for prop changes
watch(() => props.messages, (newMessages) => {
  messages.value = [...newMessages]
  if (props.autoScroll) {
    nextTick(() => scrollToBottom())
  }
}, { deep: true })
const handleScroll = (event: Event) => {
  const element = event.target as HTMLElement
  if (!element) return

  const { scrollTop, scrollHeight, clientHeight } = element
  const isNearBottom = scrollHeight - scrollTop - clientHeight < 100
  showScrollButton.value = !isNearBottom
}

// 修复滚动到底部
const scrollToBottom = () => {
  if (!scroller.value || !messages.value.length) return

  nextTick(() => {
    try {
      if (typeof scroller.value.scrollToItem === 'function') {
        scroller.value.scrollToItem(messages.value.length - 1)
      } else {
        // 备用方案
        const element = scroller.value.$el
        if (element) {
          element.scrollTop = element.scrollHeight
        }
      }
    } catch (error) {
      console.warn('Scroll to bottom failed:', error)
    }
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
  // Scroll to bottom initially if autoScroll is enabled
  if (props.autoScroll && messages.value.length > 0) {
    nextTick(() => scrollToBottom())
  }
})
</script>

<style scoped>

.chat-container {
  position: relative;
  height: 100%;
  width: 100%;
}

.chat-messages {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 16px;
}

:deep(.message-item) {
  margin-bottom: 8px;
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
