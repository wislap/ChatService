<template>
  <div class="bubble-container" ref="root">
    <div class="bubble" :class="{ 'is-mine': data.isMine }">
      <!-- 头部 -->
      <div class="bubble-header">
        <img :src="data.user.avatar" class="avatar" />
        <span class="username">
          {{ data.isAnonymous ? '匿名' : data.user.username }}
        </span>
        <span class="time">{{ formatTime(data.createdAt) }}</span>
        <button v-if="data.isMine" @click="$emit('delete', data.id)">
          删除
        </button>
      </div>

      <!-- 内容 -->
      <div class="bubble-content">
        <div class="markdown-body" v-html="renderMarkdown(data.content)" />

        <div v-if="data.images?.length" class="images">
          <img v-for="img in data.images" :key="img" :src="img" />
        </div>

        <div v-if="data.mentions?.length" class="mentions">
          <span v-for="m in data.mentions" :key="m.id">
            @{{ m.username }}
          </span>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="bubble-actions">
        <button
          class="like-btn"
          :class="{ liked: data.liked }"
          @click="$emit('like', data.id)"
        >
          ❤️ {{ data.likes }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MarkdownIt from 'markdown-it'
import * as markdownItEmoji from 'markdown-it-emoji'
import markdownItSub from 'markdown-it-sub'
import markdownItSup from 'markdown-it-sup'
import markdownItMark from 'markdown-it-mark'
import markdownItKatex from '@traptitech/markdown-it-katex'
import DOMPurify from 'dompurify'
import 'katex/dist/katex.min.css'

interface Props {
  data: {
    id: number
    user: { avatar: string; username: string }
    content: string
    images?: string[]
    mentions?: { id: number; username: string }[]
    likes: number
    liked: boolean
    isMine: boolean
    isAnonymous: boolean
    createdAt: number
  }
}

defineProps<Props>()
/*
 Use string-array form for defineEmits to avoid emitting/type issues during SFC
 compilation (some TS AST nodes like `any` can be unresolvable in the compiler
 environment). The array form is sufficient since we only emit named events.
*/
const emit = defineEmits(['like', 'delete', 'resized'])

// 配置 markdown-it
const md = new MarkdownIt({
  html: false,        // 禁止 HTML 标签
  linkify: true,      // 自动转换 URL 为链接
  typographer: true,  // 智能标点符号转换
  breaks: true        // 换行转换为 <br>
})

const resolvePlugin = (p: any) => {
  if (typeof p === 'function') return p
  if (p && typeof p.default === 'function') return p.default
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
  console.warn('[ConfessionBubble] markdown-it-emoji plugin not available or invalid')
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
  console.warn('[ConfessionBubble] markdown-it-katex plugin not available or invalid')
}

import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const renderMarkdown = (content: string) => {
  const html = md.render(content)
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'del', 'code', 'pre',
      'a', 'ul', 'ol', 'li', 'blockquote', 'h1', 'h2', 'h3',
      'h4', 'h5', 'h6', 'sub', 'sup', 'mark', 'span', 'div'
    ],
    ALLOWED_ATTR: ['href', 'class', 'style']
  })
}

// --- ResizeObserver / image load handling to notify parent scroller about size changes ---
const root = ref<HTMLElement | null>(null)
let ro: ResizeObserver | null = null

const notifyResized = async () => {
  // wait for DOM updates
  await nextTick()
  emit('resized')
}

onMounted(() => {
  // ResizeObserver to detect content size changes
  try {
    ro = new ResizeObserver(() => {
      notifyResized()
    })
    if (root.value) ro.observe(root.value)
  } catch (e) {
    // ResizeObserver may not be available in some environments
    console.warn('[ConfessionBubble] ResizeObserver unavailable:', e)
  }

  // If there are images, listen for load events to notify scroller after they load
  if (root.value) {
    const imgs = Array.from(root.value.querySelectorAll('img'))
    imgs.forEach(img => {
      if ((img as HTMLImageElement).complete) {
        // already loaded — still notify in case dimensions matter
        notifyResized()
      } else {
        const onLoad = () => {
          notifyResized()
          img.removeEventListener('load', onLoad)
        }
        img.addEventListener('load', onLoad)
      }
    })
  }
})

onBeforeUnmount(() => {
  if (ro && root.value) {
    try { ro.unobserve(root.value) } catch {}
    ro = null
  }
})

const formatTime = (timestamp: number) => {
  const diff = Date.now() - timestamp
  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour

  if (diff < minute) return '刚刚'
  if (diff < hour) return `${Math.floor(diff / minute)}分钟前`
  if (diff < day) return `${Math.floor(diff / hour)}小时前`
  return `${Math.floor(diff / day)}天前`
}
</script>

<style scoped lang="scss">
.bubble-container {
  padding: 12px 16px;
}

.bubble {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);

  &.is-mine {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
}

.bubble-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;

  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }

  .time {
    margin-left: auto;
    font-size: 12px;
    opacity: 0.6;
  }
}

.bubble-content {
  margin-bottom: 12px;

  // Markdown 样式
  .markdown-body {
    line-height: 1.6;

    :deep(p) {
      margin: 8px 0;
    }

    :deep(code) {
      background: rgba(0, 0, 0, 0.05);
      padding: 2px 6px;
      border-radius: 4px;
      font-family: 'Consolas', 'Monaco', monospace;
    }

    :deep(pre) {
      background: rgba(0, 0, 0, 0.05);
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;

      code {
        background: transparent;
        padding: 0;
      }
    }

    :deep(blockquote) {
      border-left: 4px solid #667eea;
      padding-left: 12px;
      margin: 12px 0;
      opacity: 0.8;
    }

    :deep(a) {
      color: #667eea;
      text-decoration: underline;
    }

    :deep(mark) {
      background: #fff3cd;
      padding: 2px 4px;
      border-radius: 2px;
    }

    // KaTeX 公式样式
    :deep(.katex) {
      font-size: 1.1em;
    }
  }

  .images {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;

    img {
      max-width: 120px;
      max-height: 120px;
      object-fit: cover;
      border-radius: 8px;
      cursor: pointer;
      transition: transform 0.2s;

      &:hover {
        transform: scale(1.05);
      }
    }
  }

  .mentions {
    margin-top: 8px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;

    span {
      background: rgba(102, 126, 234, 0.1);
      color: #667eea;
      padding: 2px 8px;
      border-radius: 12px;
      font-size: 14px;
      cursor: pointer;

      &:hover {
        background: rgba(102, 126, 234, 0.2);
      }
    }
  }
}

.bubble-actions {
  display: flex;
  gap: 16px;

  .like-btn {
    border: none;
    background: transparent;
    cursor: pointer;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 4px 8px;
    border-radius: 12px;
    transition: all 0.2s;

    &:hover {
      background: rgba(0, 0, 0, 0.05);
    }

    &.liked {
      color: #ff6b6b;
    }
  }
}

// 为自己发的消息调整样式
.bubble.is-mine {
  .markdown-body {
    :deep(code) {
      background: rgba(255, 255, 255, 0.2);
    }

    :deep(pre) {
      background: rgba(255, 255, 255, 0.2);
    }

    :deep(blockquote) {
      border-left-color: rgba(255, 255, 255, 0.5);
    }

    :deep(a) {
      color: #fff;
    }

    :deep(mark) {
      background: rgba(255, 243, 205, 0.3);
    }
  }

  .mentions span {
    background: rgba(255, 255, 255, 0.2);
    color: white;
  }

  .like-btn:hover {
    background: rgba(255, 255, 255, 0.2);
  }
}
</style>
