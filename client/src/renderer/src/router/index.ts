import { createRouter, createWebHashHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('@/views/auth/RegisterView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'Files',
      component: () => import('@/views/FilesView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/trash',
      name: 'Trash',
      component: () => import('@/views/TrashView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 导航守卫：未登录跳转到登录页
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    next({ name: 'Login' })
  } else if (!to.meta.requiresAuth && authStore.isLoggedIn && (to.name === 'Login' || to.name === 'Register')) {
    next({ name: 'Files' })
  } else {
    next()
  }
})

export default router
