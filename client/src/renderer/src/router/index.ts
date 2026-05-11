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
      component: () => import('@/layouts/MainLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'Files',
          component: () => import('@/views/FilesView.vue')
        },
        {
          path: 'trash',
          name: 'Trash',
          component: () => import('@/views/TrashView.vue')
        },
        {
          path: 'settings',
          name: 'Settings',
          component: () => import('@/views/settings/SettingsView.vue')
        }
      ]
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
