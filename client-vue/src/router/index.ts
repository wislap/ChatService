import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../login/LoginPage.vue'
import ChatInterface from '../ChatContainer/ChatInterface.vue'
const routes = [
  {
    path: '/',
    name: 'Home',
    component: ChatInterface

  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage
  },

]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
