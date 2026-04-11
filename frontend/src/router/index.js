import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

import Home from '../views/Home.vue';
import Login from '../views/Login.vue';

const routes = [
  { path: '/', component: Home, meta: { requiresAuth: true } },
  { path: '/login', component: Login }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  if (authStore.loading) {
    await authStore.init();
  }

  if (to.meta.requiresAuth && !authStore.user) {
    next('/login');
  } else if (to.path === '/login' && authStore.user) {
    next('/');
  } else {
    next();
  }
});

export default router;
