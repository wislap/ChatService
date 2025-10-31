import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../login/LoginPage.vue'
import FinnishRegister from '../login/FinnishRegister.vue'
import MainLayout from '../views/MainLayout.vue'
import Announcement from '../views/Announcement.vue'
import ChatInterface from '../ChatContainer/ChatInterface.vue'

const routes = [
  {
    path: '/',
    name: 'Main',
    component: MainLayout,
    children: [
      {
        path: 'announcement',
        name: 'Announcement',
        component: Announcement
      },
      {
        path: '',
        name: 'Home',
        redirect: 'announcement'
      },
      {
        path: 'login',
        name: 'Login',
        component: LoginPage
      },
      {
        path: 'FinnishRegister',
        name: 'FinnishRegister',
        component: FinnishRegister
      },
      {
        path: 'blog',
        // parent shell for blog-related pages; child routes render inside the shell's <router-view />
        component: () => import('../views/BlogShell.vue'),
        children: [
          {
            path: '',
            name: 'BlogHome',
            component: () => import('../views/blog/BlogList.vue'),
            meta: { title: 'Blog' }
          }
        ]
      },
      {
        path: 'wall',
        name: 'WallPage',
        component: () => import('../views/wall/WallPage.vue'),
        meta: { title: '表白墙' }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: ChatInterface,
        meta: { title: '聊天' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: routes,
})

export default router
