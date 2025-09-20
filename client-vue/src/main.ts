import { createApp } from 'vue'
import App from './App.vue'
import { initializeDB, cleanupDB, test } from './idb'
import router from './router/index.ts'

// Initialize the database and wait for it to complete before mounting the app
async function bootstrap() {
  try {
    cleanupDB()
    await initializeDB()
    await test()
    console.log('Database initialized successfully')

    // Clean up the database when the page is about to unload (closed or refreshed)
    window.addEventListener('beforeunload', () => {
      cleanupDB()
    })

    const app = createApp(App)
    app.use(router)
    app.mount('#app')

  } catch (error) {
    console.error('Failed to initialize database:', error)
  }
}

// Start the application bootstrap process
bootstrap()
