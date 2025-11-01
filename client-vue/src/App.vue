<template>
  <div class="app-container">
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script lang="ts">

export default {
  name: 'App',
}

</script>

<style scoped>
.app-container {
  height: 100vh;
  overflow: hidden;
}

main {
  height: 100%;
  overflow: hidden;
}
</style>
