import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// import { createPersistedState } from "pinia-persistedstate-plugin"
import App from './App.vue'
// import router from './router'
import locale from 'element-plus/dist/locale/zh-cn.js'

const app = createApp(App)
// const pinia = createPinia()
// const persist = createPersistedState()

app.use(createPinia())
// app.use(router)
// pinia.use(persist)
// app.mount('#app')
createApp(App).use(ElementPlus).mount('#app');
// app.use(ElementPlus)
