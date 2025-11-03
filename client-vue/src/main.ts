import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index.ts'

// Initialize the database and wait for it to complete before mounting the app
async function bootstrap() {

   const app = createApp(App)
    app.use(router)
    app.mount('#app')
}

// Start the application bootstrap process
bootstrap()
