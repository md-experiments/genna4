<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useSettingsStore } from './stores/settings'
import { useRouter } from 'vue-router'

const isDark = ref(false)
const showSettings = ref(false)
const authStore = useAuthStore()
const settingsStore = useSettingsStore()
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
        <button @click="showSettings = true" style="background-color: var(--primary-hover);">API Keys</button>
        <button @click="toggleTheme">{{ isDark ? 'Light' : 'Dark' }}</button>
        <button v-if="authStore.user" @click="handleLogout" style="background-color: var(--danger-color);">Logout</button>
      </div>
    </header>
    <main>
      <router-view />
    </main>

    <!-- Ephemeral Settings Modal -->
    <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
      <div class="card modal-content">
        <h2>API Settings</h2>
        <p style="font-size: 0.85rem; color: var(--danger-color); margin-bottom: 1rem;">
          These keys are stored securely in your browser's RAM for this session only. They will be wiped if you refresh or close the tab, and are only securely transmitted via HTTPS.
        </p>

        <label style="display:block; margin-bottom: 0.5rem; font-weight: 600;">OpenRouter Key</label>
        <input type="password" v-model="settingsStore.openrouterKey" placeholder="sk-or-v1-..." class="input-field" />

        <label style="display:block; margin-bottom: 0.5rem; font-weight: 600;">OpenAI Key</label>
        <input type="password" v-model="settingsStore.openaiKey" placeholder="sk-..." class="input-field" />

        <label style="display:block; margin-bottom: 0.5rem; font-weight: 600;">Anthropic Key</label>
        <input type="password" v-model="settingsStore.anthropicKey" placeholder="sk-ant-..." class="input-field" />

        <div style="display: flex; justify-content: flex-end; margin-top: 1rem;">
          <button @click="showSettings = false">Done</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}
.modal-content {
  width: 90%;
  max-width: 500px;
}
.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 2rem;
}
</style>
