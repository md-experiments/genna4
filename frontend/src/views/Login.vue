<template>
  <div class="card" style="max-width: 400px; margin: 4rem auto;">
    <h2>Login to Genna</h2>
    <form @submit.prevent="handleLogin" style="margin-top: 1.5rem;">
      <div v-if="error" class="error-msg">{{ error }}</div>
      <input type="email" class="input-field" v-model="email" placeholder="Email" required />
      <input type="password" class="input-field" v-model="password" placeholder="Password" required />
      <button type="submit" style="width: 100%; margin-bottom: 1rem;">Sign In with Email</button>
      
      <div style="text-align: center; margin-bottom: 1rem; font-size: 0.9rem; color: var(--text-color-secondary);">
        OR
      </div>
      
      <button type="button" @click="handleGoogleLogin" style="width: 100%; background-color: #4285F4; color: white;">
        Sign In with Google
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const error = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
  error.value = '';
  try {
    await authStore.login(email.value, password.value);
    router.push('/');
  } catch (err) {
    error.value = err.message || 'Login failed.';
  }
};

const handleGoogleLogin = async () => {
  error.value = '';
  try {
    await authStore.loginWithGoogle();
    router.push('/');
  } catch (err) {
    error.value = err.message || 'Google login failed.';
  }
};
</script>

<style scoped>
.error-msg {
  color: var(--danger-color);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
</style>
