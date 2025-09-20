<template>
  <div class="app-container" >
    <h1 class="app-title">聊天界面</h1>
    <p><strong>Current route path:</strong> {{ $route.fullPath }}</p>
    <nav>
    <RouterLink to="/">Go to Home</RouterLink>
    <RouterLink to="/login">Go to login</RouterLink>
  </nav>
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
