<template>
  <div class="main-layout">
    <aside :class="['sidebar', { open: sidebarOpen }]">
      <div class="sidebar-header">
        <div class="logo">ChatService</div>
        <div class="tagline">工具与公告</div>
      </div>

      <nav class="sidebar-nav">
        <ul>
          <li class="nav-item">
            <RouterLink to="/announcement" class="nav-link" active-class="active">
              <span class="nav-marker" aria-hidden="true"></span>
              <span class="nav-label">公告</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/blog" class="nav-link" active-class="active">
              <span class="nav-marker" aria-hidden="true"></span>
              <span class="nav-label">Blog（预留）</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/wall" class="nav-link" active-class="active">
              <span class="nav-marker" aria-hidden="true"></span>
              <span class="nav-label">表白墙</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/chat" class="nav-link" active-class="active">
              <span class="nav-marker" aria-hidden="true"></span>
              <span class="nav-label">聊天</span>
            </RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink to="/login" class="nav-link" active-class="active">
              <span class="nav-marker" aria-hidden="true"></span>
              <span class="nav-label">登录</span>
            </RouterLink>
          </li>
        </ul>
      </nav>
    </aside>

    <main :class="['content-area', { 'sidebar-open': sidebarOpen }]">
      <Transition name="fade" mode="in-out">
        <RouterView />
      </Transition>
    </main>

    <!-- Hamburger button fixed at bottom-left -->
    <button class="hamburger" @click="toggleSidebar" aria-label="Toggle sidebar">
      <!-- inline SVG hamburger icon -->
      <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
        <path d="M3 6h18a1 1 0 000-2H3a1 1 0 000 2zm18 7H3a1 1 0 000 2h18a1 1 0 000-2zm0 7H3a1 1 0 000 2h18a1 1 0 000-2z"/>
      </svg>
    </button>

    <!-- overlay for small screens when sidebar is open -->
    <div v-if="sidebarOpen" class="overlay" @click="closeSidebar"></div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const sidebarOpen = ref(false)

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const closeSidebar = () => {
  sidebarOpen.value = false
}
</script>

<style scoped>
.main-layout {
  display: flex;
  min-height: 100vh;
  box-sizing: border-box;
  position: relative;
}

/* Sidebar */
.sidebar {
  width: 220px;
  padding: 20px;
  box-sizing: border-box;
  transition: transform 0.25s ease, opacity 0.25s ease;
  transform: translateX(-100%);
  opacity: 0;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 30;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); /* match auth gradient */
  color: white;
  border-right: none;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}
.sidebar.open {
  transform: translateX(0);
  opacity: 1;
}

/* Sidebar header */
.sidebar-header {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 18px;
}
.logo {
  font-weight: 700;
  font-size: 18px;
  color: #ffffff;
}
.tagline {
  font-size: 12px;
  color: rgba(255,255,255,0.9);
}

/* Navigation */
.sidebar-nav {
  background: rgba(255,255,255,0.04);
  border-radius: 10px;
  padding: 8px;
}
.sidebar-nav ul {
  list-style: none;
  padding: 6px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.nav-item {
  display: flex;
}
.nav-marker {
  width: 8px;
  height: 8px;
  background: rgba(255,255,255,0.28);
  border-radius: 50%;
  margin-right: 10px;
  flex-shrink: 0;
  transition: background 0.15s, transform 0.12s;
  align-self: center;
}
.nav-link {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  color: rgba(255,255,255,0.95);
  text-decoration: none;
  transition: background 0.15s, transform 0.08s;
  width: 100%;
}
.nav-link .nav-label {
  margin-left: 4px;
  font-weight: 600;
}
.nav-link:hover {
  background: rgba(255,255,255,0.06);
  transform: translateY(-1px);
}
.nav-link.active {
  background: rgba(255,255,255,0.92);
  color: #4c51bf;
  box-shadow: 0 2px 6px rgba(0,0,0,0.12);
}
.nav-link.active .nav-marker {
  background: #4c51bf;
  transform: scale(1.15);
}

/* Remove previous actions area on sidebar */
.actions {
  display: none;
}

/* Desktop: keep sidebar as overlay; when open push content by margin-left */
@media (min-width: 900px) {
  /* keep sidebar fixed (not in document flow) so it doesn't reserve space when hidden */
  .sidebar {
    position: fixed;
    transform: translateX(-100%);
    opacity: 0;
  }

  .sidebar.open {
    transform: translateX(0);
    opacity: 1;
  }

  .sidebar:not(.open) {
    pointer-events: none;
  }

  /* push content only when sidebar is open */
  .content-area.sidebar-open {
    margin-left: 220px;
  }
}

/* Content area */
.content-area {
  flex: 1;
  padding: 24px;
  box-sizing: border-box;
  transition: margin-left 0.25s ease;
}

/* Route transition: simple fade to reduce perceived flicker */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 180ms ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.fade-enter-to,
.fade-leave-from {
  opacity: 1;
}

/* Hamburger button */
.hamburger {
  position: fixed;
  left: 16px;
  bottom: 16px;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  background: rgba(76,81,191,0.95); /* match sidebar/main theme */
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  padding: 8px;
  z-index: 60;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(76,81,191,0.12);
}
.hamburger svg {
  width: 20px;
  height: 20px;
  fill: white;
  display: block;
}
.hamburger .bar {
  display: none;
}
.hamburger.alt {
  background: rgba(76,81,191,0.95);
}

/* Overlay when sidebar open on small screens */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 20;
}

/* Small screens: sidebar overlays content; large screens: sidebar shown/hidden layout handled above */
@media (min-width: 900px) {
  .overlay {
    display: none;
  }
}
</style>
