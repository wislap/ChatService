<template>
  <div class="app-container">
    <h1 class="app-title">聊天界面</h1>
    <ChatInterface />
  </div>
</template>

<script lang="ts">
import ChatInterface from './components/ChatInterface.vue'

export default {
  name: 'App',
  components: {
    ChatInterface
  }
}


</script>
