<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const isDark = ref(false)
const authStore = useAuthStore()
const router = useRouter()

const toggleTheme = () => {
  isDark.value = !isDark.value
  document.documentElement.setAttribute('data-theme', isDark.value ? 'dark' : 'light')
}

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}

onMounted(() => {
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    isDark.value = true
    document.documentElement.setAttribute('data-theme', 'dark')
  }
})
</script>

<template>
  <div class="container">
    <header class="app-header">
      <div style="display: flex; align-items: baseline; gap: 1rem;">
        <h1>Genna</h1>
        <span style="font-size: 0.9rem; color: var(--text-color-secondary)">Annotation System</span>
      </div>
      <div style="display: flex; gap: 1rem; align-items: center;">
        <button @click="toggleTheme">{{ isDark ? 'Light' : 'Dark' }}</button>
        <button v-if="authStore.user" @click="handleLogout" style="background-color: var(--danger-color);">Logout</button>
      </div>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<style scoped>
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 2rem;
}
</style>
