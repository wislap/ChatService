<template>
  <div class="finish-register-container">
    <h2>注册成功！</h2>
    <p>您的账户已成功创建。</p>
    <button @click="goToHome">返回首页</button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

const goToHome = () => {
  router.push('/');
};
</script>

<style scoped>
.finish-register-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100vh;
  text-align: center;
  background-color: #f0f2f5;
}

h2 {
  color: #42b983;
  margin-bottom: 1rem;
}

p {
  margin-bottom: 2rem;
  color: #333;
}

button {
  padding: 10px 20px;
  font-size: 1rem;
  color: #fff;
  background-color: #42b983;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #36a476;
}
</style>
