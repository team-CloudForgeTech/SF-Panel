import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import axios from 'axios'

const app = createApp(App)

app.config.errorHandler = (err) => {
  console.error('全局错误:', err)
}

// 注册所有图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 配置axios默认值
axios.defaults.baseURL = 'http://localhost:5000'

// 使用插件
app.use(ElementPlus)
app.use(router)

// 挂载应用
app.mount('#app')
// 在现有代码下方添加
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
