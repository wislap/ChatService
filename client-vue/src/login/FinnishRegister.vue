<template>
  <div class="finish-register-container">
    <div v-if="verificationStatus === 'pending'">
      <h2>正在验证您的邮箱...</h2>
      <p>请稍候，我们正在完成注册的最后一步。</p>
    </div>
    <div v-else-if="verificationStatus === 'success'">
      <h2>注册成功！</h2>
      <p>您的账户已成功激活。将在 {{ countdown }} 秒后返回首页。</p>
      <button @click="goToHome">立即返回首页</button>
    </div>
    <div v-else-if="verificationStatus === 'error'">
      <h2>验证失败</h2>
      <p>{{ errorMessage }}</p>
      <button @click="goToHome">返回首页</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import api from '@/utils/api';

const router = useRouter();
const route = useRoute();

const verificationStatus = ref('pending'); // 'pending', 'success', 'error'
const errorMessage = ref('无法验证您的邮箱，链接可能已失效或被使用。');
const countdown = ref(5);

const goToHome = () => {
  router.push('/');
};

const startCountdown = () => {
  const interval = setInterval(() => {
    countdown.value -= 1;
    if (countdown.value <= 0) {
      clearInterval(interval);
      goToHome();
    }
  }, 1000);
};

onMounted(async () => {
  const token = route.query.token as string;

  if (!token) {
    verificationStatus.value = 'error';
    errorMessage.value = '未提供验证令牌。';
    return;
  }

  try {
    await api.get(`/user/verify-email/?token=${token}`);
    verificationStatus.value = 'success';
    startCountdown();
  } catch (error: unknown) {
    verificationStatus.value = 'error';
    const axiosError = error as { response?: { data?: { detail?: string } } };
    if (axiosError.response?.data?.detail) {
      errorMessage.value = axiosError.response.data.detail;
    }
    console.error('Email verification failed:', error);
  }
});
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
