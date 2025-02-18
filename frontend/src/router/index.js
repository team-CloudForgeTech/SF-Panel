import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/Login.vue')
    },
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('../views/Dashboard.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/file-manager',
      name: 'FileManager',
      component: () => import('../views/FileManager.vue')
    },
    {
      path: '/process-manager',
      name: 'ProcessManager',
      component: () => import('../views/ProcessManager.vue')
    },
    {
      path: '/shell-terminal',
      name: 'ShellTerminal',
      component: () => import('../views/ShellTerminal.vue')
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router