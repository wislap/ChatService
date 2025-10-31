<template>
  <div class="chat-container">
    <!-- 虚拟滚动区域 -->
    <div class="virtual-scroll-area">
      <DynamicScroller
        :items="messages"
        :min-item-size="80"
        key-field="id"
        v-slot="{ item, index, active }"
        ref="scroller"
        @scroll="handleScroll"
        class="scroller"
      >
        <DynamicScrollerItem
          :item="item"
          :active="active"
          :size-dependencies="[item.content]"
          :data-index="index"
          class="scroller-item"
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
        </DynamicScrollerItem>
      </DynamicScroller>
    </div>

    <!-- 滚动到底部按钮 -->
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
import { DynamicScroller, DynamicScrollerItem } from 'vue-virtual-scroller'
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

const scrollToBottom = () => {
  if (!scroller.value || !messages.value.length) return

  nextTick(() => {
    try {
      scroller.value.scrollToBottom()
    } catch (error) {
      console.warn('Scroll to bottom failed:', error)
    }
  })
}

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
    emit('messageDelete', messageId)
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
  if (props.autoScroll && messages.value.length > 0) {
    nextTick(() => scrollToBottom())
  }
})
</script>

<style scoped>
/* 最外层容器 - 移除边框，由ChatInterface提供视觉框架 */
.chat-container {
  position: relative;
  height: 100%;
  width: 100%;
  background: transparent;
  overflow: hidden;
}

/* 虚拟滚动区域 */
.virtual-scroll-area {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px;
  background: transparent;
  box-sizing: border-box;
}

/* 虚拟滚动组件 */
.scroller {
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  overflow-y: auto;
}

/* 自定义滚动条 */
.scroller::-webkit-scrollbar {
  width: 10px;
}

.scroller::-webkit-scrollbar-track {
  background: rgba(226, 232, 240, 0.5);
  border-radius: 5px;
}

.scroller::-webkit-scrollbar-thumb {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-radius: 5px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.scroller::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
  background-clip: content-box;
}

/* 滚动项样式 */
.scroller-item {
  padding: 16px 20px;
  margin-bottom: 12px;
  box-sizing: border-box;
}

:deep(.message-item) {
  margin-bottom: 12px;
}

:deep(.vue-recycle-scroller__item-view) {
  margin-bottom: 32px;
}

/* 滚动到底部按钮 - 保持原有样式 */
.scroll-to-bottom {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  font-size: 20px;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.scroll-to-bottom:hover {
  background: linear-gradient(135deg, #5a67d8, #6b46c1);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.scroll-to-bottom:active {
  transform: translateY(0) scale(0.95);
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
}

/* Custom button styles */
.custom-button {
  /* Inherits base styles from MessageBubble component */
}

/* 响应式设计 */
@media (max-width: 768px) {
  .virtual-scroll-area {
    padding: 16px;
  }

  .scroll-to-bottom {
    width: 42px;
    height: 42px;
    font-size: 18px;
    bottom: 20px;
    right: 20px;
  }
}
</style>
