<template>
  <div class="dashboard">
    <div class="card mt-4">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2>Datasets</h2>
        <button @click="uploadDataset">Upload Dataset</button>
      </div>
      <p style="color: var(--text-color-secondary);">No datasets found. Upload one to get started.</p>
    </div>

    <div class="card mt-4">
      <h2>Annotation Activity</h2>
      <p style="color: var(--text-color-secondary);">Select a dataset to begin annotating and comparing AI responses.</p>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const uploadDataset = () => {
  // Logic to upload dataset
  console.log("Upload dataset clicked");
};
</script>

<style scoped>
.mt-4 { margin-top: 2rem; }
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
</style>
