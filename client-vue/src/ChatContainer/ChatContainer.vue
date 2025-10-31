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
            @like="handleLike"
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

    <!-- 滚动到顶部按钮 -->
    <button
      v-if="showScrollButton"
      @click="scrollToTop"
      class="scroll-to-top"
      title="滚动到顶部"
    >
      ⬆
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
  likes?: number
  liked?: boolean
}

interface Props {
  messages?: ExtendedMessageData[]
  autoScroll?: boolean
  currentUserId?: string
}

const props = withDefaults(defineProps<Props>(), {
  messages: () => [],
  autoScroll: false, // 表白墙不需要自动滚动到最新（因为最新已经在上面）
  currentUserId: 'current-user'
})

const emit = defineEmits<{
  messageLike: [messageId: string]
  messageDelete: [messageId: string]
  messagesChange: [messages: ExtendedMessageData[]]
}>()

// Reactive data
const scroller = ref()
const showScrollButton = ref(false)
const messages = ref<ExtendedMessageData[]>([...props.messages])

// Watch for prop changes
watch(() => props.messages, (newMessages) => {
  messages.value = [...newMessages]
}, { deep: true })

const handleScroll = (event: Event) => {
  const element = event.target as HTMLElement
  if (!element) return

  const { scrollTop } = element
  // 在表白墙中，最新消息在顶部，所以当滚动位置不在顶部时显示按钮
  const isNearTop = scrollTop < 100
  showScrollButton.value = !isNearTop
}

const scrollToTop = () => {
  if (!scroller.value || !messages.value.length) return

  nextTick(() => {
    try {
      // 方案1：尝试使用API方法
      if (scroller.value.scrollToItem && messages.value.length > 0) {
        scroller.value.scrollToItem(messages.value[0])
        return
      }

      // 方案2：查找滚动容器并使用平滑滚动
      const scrollContainer = findScrollContainer()
      if (scrollContainer) {
        smoothScrollToTop(scrollContainer)
        return
      }

      // 方案3：直接操作DOM
      const element = scroller.value?.$el
      if (element) {
        element.scrollTop = 0
      }
    } catch (error) {
      console.warn('Scroll to top failed:', error)
      // 最后的备选方案
      const element = scroller.value?.$el
      if (element) {
        element.scrollTop = 0
      }
    }
  })
}

// 查找滚动容器
const findScrollContainer = (): HTMLElement | null => {
  if (!scroller.value) return null

  // 尝试多种方式获取滚动容器
  const container = scroller.value.$el?.querySelector('.vue-recycle-scroller') as HTMLElement
  if (container && container.scrollTop !== undefined) {
    return container
  }

  // 备选：使用组件本身的DOM
  const el = scroller.value.$el as HTMLElement
  if (el && el.scrollTop !== undefined) {
    return el
  }

  return null
}

// 平滑滚动到顶部
const smoothScrollToTop = (container: HTMLElement) => {
  const currentScrollTop = container.scrollTop
  const duration = 600 // 动画持续时间（毫秒）
  const startTime = performance.now()

  const animateScroll = (currentTime: number) => {
    const elapsed = currentTime - startTime
    const progress = Math.min(elapsed / duration, 1)

    // 使用easeOutCubic缓动函数
    const easeProgress = 1 - Math.pow(1 - progress, 3)
    const newScrollTop = currentScrollTop * (1 - easeProgress)

    container.scrollTop = newScrollTop

    if (progress < 1) {
      requestAnimationFrame(animateScroll)
    }
  }

  // 检查是否支持现代滚动API
  if ('scrollBehavior' in document.documentElement.style && container.scrollTo) {
    container.scrollTo({ top: 0, behavior: 'smooth' })
  } else {
    // 使用自定义动画
    requestAnimationFrame(animateScroll)
  }
}

const getMessageVariant = (message: ExtendedMessageData): 'sent' | 'received' | 'system' => {
  if (message.sender === 'system') return 'system'
  if (message.sender === props.currentUserId) return 'sent'
  return 'received'
}

// Event handlers
const handleLike = (messageId: string) => {
  emit('messageLike', messageId)
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
  scrollToTop
})

onMounted(() => {
  // 表白墙不需要初始化滚动，因为消息按时间倒序，最新的在上面
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
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  border-radius: 5px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.scroller::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(135deg, #ff5252, #e53e3e);
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

/* 滚动到顶部按钮 - 表白墙风格 */
.scroll-to-top {
  position: absolute;
  bottom: 24px;
  right: 24px;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ee5a52);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 16px rgba(255, 107, 107, 0.4);
  transition: all 0.3s ease;
  font-size: 20px;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.scroll-to-top:hover {
  background: linear-gradient(135deg, #ff5252, #e53e3e);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(255, 107, 107, 0.6);
}

.scroll-to-top:active {
  transform: translateY(0) scale(0.95);
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
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

  .scroll-to-top {
    width: 42px;
    height: 42px;
    font-size: 18px;
    bottom: 20px;
    right: 20px;
  }
}
</style>
