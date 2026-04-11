<template>
  <div class="card" style="max-width: 400px; margin: 4rem auto;">
    <h2>Login to Genna</h2>
    <form @submit.prevent="handleLogin" style="margin-top: 1.5rem;">
      <div v-if="error" class="error-msg">{{ error }}</div>
      <input type="email" class="input-field" v-model="email" placeholder="Email" required />
      <input type="password" class="input-field" v-model="password" placeholder="Password" required />
      <button type="submit" style="width: 100%;">Sign In</button>
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
</script>

<style scoped>
.error-msg {
  color: var(--danger-color);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}
</style>
