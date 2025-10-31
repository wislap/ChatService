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

    <!-- Button area -->
    <div class="button-area" v-if="showButtons">
      <slot name="buttons">
        <button
          v-if="editable"
          @click="$emit('edit', message.id)"
          class="action-button edit-button"
        >
          Edit
        </button>
        <button
          @click="$emit('copy', message.content)"
          class="action-button copy-button"
        >
          Copy
        </button>
        <button
          @click="$emit('delete', message.id)"
          class="action-button delete-button"
        >
          Delete
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
  edit: [messageId: string]
  copy: [content: string]
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

const resolvePlugin = (p: unknown): Function | null => {
  if (typeof p === 'function') return p
  if (p && typeof (p as any).default === 'function') return (p as any).default
  return null
}

const emojiPlugin = resolvePlugin(markdownItEmoji)
const subPlugin = resolvePlugin(markdownItSub)
const supPlugin = resolvePlugin(markdownItSup)
const markPlugin = resolvePlugin(markdownItMark)
const katexPlugin = resolvePlugin(markdownItKatex)

// 注册插件（有的包在不同打包方式下导出可能不同，先检查再 use）
if (emojiPlugin) {
  md.use(emojiPlugin) // 表情支持 :smile:
} else {
  console.warn('[MessageBubble] markdown-it-emoji plugin not available or invalid')
}
if (subPlugin) md.use(subPlugin)        // 下标 H~2~O
if (supPlugin) md.use(supPlugin)        // 上标 X^2^
if (markPlugin) md.use(markPlugin)      // 高亮 ==marked==
if (katexPlugin) {
  md.use(katexPlugin, {    // LaTeX 数学公式
    throwOnError: false,
    errorColor: '#cc0000'
  })
} else {
  console.warn('[MessageBubble] markdown-it-katex plugin not available or invalid')
}

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
  const rendered = md.render(props.message.content)
  return DOMPurify.sanitize(rendered, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'del', 'code', 'pre',
      'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3',
      'h4', 'h5', 'h6', 'sub', 'sup', 'mark', 'span', 'div'
    ],
    ALLOWED_ATTR: ['href', 'class', 'style']
  })
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
  margin: 8px 0; /* 移除左右margin，只保留上下间距 */
  width: 100%; /* 设置统一宽度为100% */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  position: relative;
  box-sizing: border-box; /* 确保padding不增加总宽度 */
}

.message-bubble:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Variant styles */
.message-sent {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
}

.message-received {
  background: #f8f9fa;
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
  border-left: 4px solid #007bff;
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
  gap: 8px;
  justify-content: flex-end;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.message-sent .button-area {
  border-top-color: rgba(255, 255, 255, 0.2);
}

.action-button {
  padding: 4px 12px;
  border: none;
  border-radius: 12px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  background: rgba(0, 0, 0, 0.1);
  color: inherit;
}

.message-sent .action-button {
  background: rgba(255, 255, 255, 0.2);
}

.action-button:hover {
  transform: translateY(-1px);
  opacity: 0.8;
}

.edit-button:hover {
  background: #28a745;
  color: white;
}

.copy-button:hover {
  background: #17a2b8;
  color: white;
}

.delete-button:hover {
  background: #dc3545;
  color: white;
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
