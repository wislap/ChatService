<template>
  <div class="message-bubble" :class="bubbleClass">
    <!-- Header with timestamp, sender, and message ID -->
    <div class="message-header">
      <div class="message-meta">
        <span class="sender">{{ message.sender }}</span>
        <span class="message-id">ID: {{ message.id }}</span>
      </div>
      <div class="timestamp">{{ formatTimestamp(message.timestamp) }}</div>
    </div>

    <!-- Message content with markdown rendering -->
    <div class="message-content">
      <div
        v-if="message.type === 'markdown'"
        class="markdown-content"
        v-html="renderedMarkdown"
      ></div>
      <div v-else-if="message.type === 'text'" class="text-content">
        {{ message.content }}
      </div>
      <div v-else-if="message.type === 'image'" class="image-content">
        <img :src="message.content" :alt="message.alt || 'Image'" />
      </div>
      <div v-else class="unknown-content">
        <span>Unsupported message type: {{ message.type }}</span>
      </div>
    </div>

    <!-- Button area - 改为表白墙功能 -->
    <div class="button-area" v-if="showButtons">
      <slot name="buttons">
        <button
          @click="$emit('like', message.id)"
          class="action-button like-button"
          :class="{ liked: message.liked }"
        >
          ❤️ {{ message.likes || 0 }}
        </button>
        <button
          @click="$emit('delete', message.id)"
          class="action-button delete-button"
        >
          删除
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MarkdownIt from 'markdown-it'
import * as markdownItEmoji from 'markdown-it-emoji'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItMark from 'markdown-it-mark'
import markdownItKatex from '@traptitech/markdown-it-katex'
import hljs from 'highlight.js/lib/core'
import 'highlight.js/styles/github.css'
import DOMPurify from 'dompurify'
import 'katex/dist/katex.min.css'

// Import commonly used languages for highlight.js
import javascript from 'highlight.js/lib/languages/javascript'
import typescript from 'highlight.js/lib/languages/typescript'
import python from 'highlight.js/lib/languages/python'
import css from 'highlight.js/lib/languages/css'
import html from 'highlight.js/lib/languages/xml'

// Register languages
hljs.registerLanguage('javascript', javascript)
hljs.registerLanguage('typescript', typescript)
hljs.registerLanguage('python', python)
hljs.registerLanguage('css', css)
hljs.registerLanguage('html', html)

export interface MessageData {
  id: string
  sender: string
  content: string
  timestamp: number | Date
  type: 'markdown' | 'text' | 'image' | string
  alt?: string
  likes?: number
  liked?: boolean
}

interface Props {
  message: MessageData
  variant?: 'sent' | 'received' | 'system'
  editable?: boolean
  showButtons?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'received',
  editable: true,
  showButtons: true
})

defineEmits<{
  like: [messageId: string]
  delete: [messageId: string]
}>()

// 配置 markdown-it
const md = new MarkdownIt({
  html: false,        // 禁止 HTML 标签
  linkify: true,      // 自动转换 URL 为链接
  typographer: true,  // 智能标点符号转换
  breaks: true,       // 换行转换为 <br>
  highlight: function (str: string, lang: string) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(str, { language: lang }).value
      } catch {
        // Ignore errors
      }
    }
    return '' // Use external default escaping
  }
})

// 插件解析函数（修复emoji支持 - 使用更通用的方式）
const resolvePlugin = (p: unknown): Function | null => {
  if (typeof p === 'function') return p
  if (p && typeof (p as any).default === 'function') return (p as any).default

  // 特殊处理emoji插件 - 尝试常见的属性名
  if (p && typeof p === 'object' && p !== null) {
    const obj = p as any
    // 尝试常见的markdown-it插件属性名
    const possibleKeys = ['replace', 'render', 'plugin', 'default', 'emoji']

    for (const key of possibleKeys) {
      if (key in obj && typeof obj[key] === 'function') {
        console.log(`[MessageBubble] Found ${key} function in plugin object, using it`)
        return obj[key]
      }
    }

    // 如果没有找到函数，检查是否是数组中的第一个元素
    if (Array.isArray(obj) && obj.length > 0 && typeof obj[0] === 'function') {
      console.log('[MessageBubble] Found function in array[0], using it')
      return obj[0]
    }
  }

  return null
}

const emojiPlugin = resolvePlugin(markdownItEmoji)
const subPlugin = resolvePlugin(markdownItSub)
const supPlugin = resolvePlugin(markdownItSup)
const markPlugin = resolvePlugin(markdownItMark)
const katexPlugin = resolvePlugin(markdownItKatex)

// 注册插件（带错误处理和类型断言）
const registerPlugins = () => {
  try {
    if (emojiPlugin) {
      console.log('[MessageBubble] Registering emoji plugin')
      md.use(emojiPlugin as any) // 表情支持 :smile:
    } else {
      console.warn('[MessageBubble] markdown-it-emoji plugin not available or invalid')
    }
    if (subPlugin) {
      console.log('[MessageBubble] Registering sub plugin')
      md.use(subPlugin as any)        // 下标 H~2~O
    }
    if (supPlugin) {
      console.log('[MessageBubble] Registering sup plugin')
      md.use(supPlugin as any)        // 上标 X^2^
    }
    if (markPlugin) {
      console.log('[MessageBubble] Registering mark plugin')
      md.use(markPlugin as any)      // 高亮 ==marked==
    }
    if (katexPlugin) {
      console.log('[MessageBubble] Registering katex plugin')
      md.use(katexPlugin as any, {    // LaTeX 数学公式
        throwOnError: false,
        errorColor: '#cc0000'
      })
    } else {
      console.warn('[MessageBubble] markdown-it-katex plugin not available or invalid')
    }
  } catch (error) {
    console.warn('[MessageBubble] Failed to register plugins:', error)
  }
}

// 立即注册插件
registerPlugins()

// Computed properties
const bubbleClass = computed(() => {
  return {
    'message-sent': props.variant === 'sent',
    'message-received': props.variant === 'received',
    'message-system': props.variant === 'system',
    [`message-type-${props.message.type}`]: true
  }
})

const renderedMarkdown = computed(() => {
  if (props.message.type !== 'markdown') return ''

  try {
    const rendered = md.render(props.message.content)
    return DOMPurify.sanitize(rendered, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'del', 'code', 'pre',
        'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3',
        'h4', 'h5', 'h6', 'sub', 'sup', 'mark', 'span', 'div'
      ],
      ALLOWED_ATTR: ['href', 'class', 'style']
    })
  } catch (error) {
    console.warn('[MessageBubble] Failed to render markdown:', error)
    return DOMPurify.sanitize(props.message.content)
  }
})

// Utility functions
const formatTimestamp = (timestamp: number | Date): string => {
  const date = typeof timestamp === 'number' ? new Date(timestamp) : timestamp
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}
</script>

<style scoped>
.message-bubble {
  border-radius: 16px;
  padding: 12px 16px;
  margin: 8px 0;
  width: 100%;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  position: relative;
  box-sizing: border-box;
  background: #fff;
  border: 1px solid #e9ecef;
}

.message-bubble:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Variant styles - 调整为表白墙风格 */
.message-sent {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
}

.message-received {
  background: #fff;
  color: #212529;
  border: 1px solid #e9ecef;
}

.message-system {
  background: #fff3cd;
  color: #856404;
  border: 1px solid #ffeaa7;
  text-align: center;
  font-style: italic;
}

/* Header styles */
.message-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 0.85rem;
  opacity: 0.8;
}

.message-meta {
  display: flex;
  gap: 12px;
}

.sender {
  font-weight: 600;
}

.message-id {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.timestamp {
  font-size: 0.75rem;
  white-space: nowrap;
}

/* Content styles */
.message-content {
  line-height: 1.6;
  word-wrap: break-word;
  margin-bottom: 12px;
}

.markdown-content {
  /* Markdown-specific styles */
}

.markdown-content :deep(p) {
  margin: 8px 0;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin: 12px 0 8px 0;
  font-weight: 600;
}

.markdown-content :deep(pre) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 8px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
}

.message-sent .markdown-content :deep(pre) {
  background: rgba(255, 255, 255, 0.15);
}

.markdown-content :deep(code) {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 4px;
  padding: 2px 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.message-sent .markdown-content :deep(code) {
  background: rgba(255, 255, 255, 0.2);
}

.markdown-content :deep(blockquote) {
  border-left: 4px solid #667eea;
  margin: 8px 0;
  padding-left: 12px;
  opacity: 0.8;
}

.message-sent .markdown-content :deep(blockquote) {
  border-left-color: rgba(255, 255, 255, 0.5);
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 8px 0;
  padding-left: 24px;
}

/* Emoji styles */
.markdown-content :deep(.emoji) {
  vertical-align: middle;
  width: 1.2em;
  height: 1.2em;
}

/* Mark (highlight) styles */
.markdown-content :deep(mark) {
  background: #fff3cd;
  padding: 2px 4px;
  border-radius: 2px;
}

.message-sent .markdown-content :deep(mark) {
  background: rgba(255, 243, 205, 0.3);
}

/* KaTeX styles */
.markdown-content :deep(.katex) {
  font-size: 1.1em;
}

.markdown-content :deep(.katex-display) {
  margin: 12px 0;
  text-align: center;
}

.text-content {
  white-space: pre-wrap;
}

.image-content img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

.unknown-content {
  font-style: italic;
  opacity: 0.6;
}

/* Button area styles */
.button-area {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.message-sent .button-area {
  border-top-color: rgba(255, 255, 255, 0.2);
}

.action-button {
  padding: 4px 8px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: transparent;
  color: inherit;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-button:hover {
  background: rgba(0, 0, 0, 0.05);
  transform: translateY(-1px);
}

.message-sent .action-button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.like-button:hover {
  color: #ff6b6b;
}

.like-button.liked {
  color: #ff6b6b;
}

.delete-button:hover {
  background: rgba(220, 53, 69, 0.1);
  color: #dc3545;
}

/* Type-specific styles */
.message-type-markdown {
  /* Additional styles for markdown messages */
}

.message-type-text {
  /* Additional styles for text messages */
}

.message-type-image {
  /* Additional styles for image messages */
}
</style>
