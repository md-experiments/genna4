<template>
  <div class="dashboard">
    <div class="card mt-4">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2>Datasets</h2>
        <button @click="showModal = true">New Dataset</button>
      </div>
      <p style="color: var(--text-color-secondary);">No datasets found. Create or upload one to get started.</p>
    </div>

    <div class="card mt-4">
      <h2>Annotation Activity</h2>
      <p style="color: var(--text-color-secondary);">Select a dataset to begin annotating and comparing AI responses.</p>
    </div>

    <!-- Dataset Creation Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="card modal-content">
        <h2 style="margin-bottom: 1rem;">Add Dataset</h2>
        
        <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem;">
          <button :style="tab === 'upload' ? 'background: var(--primary-hover);' : 'background: transparent; color: var(--text-color);'" @click="tab = 'upload'">Upload File</button>
          <button :style="tab === 'manual' ? 'background: var(--primary-hover);' : 'background: transparent; color: var(--text-color);'" @click="tab = 'manual'">Manual Entry</button>
        </div>

        <!-- Upload Tab -->
        <div v-if="tab === 'upload'">
          <input type="file" ref="fileInput" @change="handleFileUpload" accept=".json,.csv" style="display: none" />
          <p style="margin-bottom: 1rem; color: var(--text-color-secondary);">Upload a JSON or CSV file containing your dataset rows.</p>
          <button @click="triggerFileInput" style="width: 100%;">Select & Upload File</button>
        </div>

        <!-- Manual Entry Tab -->
        <div v-if="tab === 'manual'">
          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Dataset Name</label>
          <input type="text" v-model="manualName" placeholder="My Dataset" class="input-field" />

          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Columns (comma separated)</label>
          <input type="text" v-model="manualColumns" placeholder="id, content, label" class="input-field" />

          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Data (one row per line, comma separated)</label>
          <textarea v-model="manualData" rows="6" class="input-field" placeholder="1, The stock market crashed, Finance&#10;2, The new iPhone is great, Tech" style="resize: vertical; font-family: monospace;"></textarea>

          <button @click="submitManualDataset" style="width: 100%;">Create Dataset</button>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const showModal = ref(false);
const tab = ref('upload');

const fileInput = ref(null);
const manualName = ref('');
const manualColumns = ref('');
const manualData = ref('');

const triggerFileInput = () => {
  if (fileInput.value) fileInput.value.click();
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append('file', file);

  try {
    const token = await authStore.user.getIdToken();
    const res = await fetch('http://localhost:8000/api/datasets/upload', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` },
      body: formData
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    alert(`Successfully uploaded ${data.row_count} rows!`);
    showModal.value = false;
  } catch (err) {
    alert("Error uploading dataset: " + err.message);
  } finally {
    if (fileInput.value) fileInput.value.value = '';
  }
};

const submitManualDataset = async () => {
  if (!manualName.value || !manualColumns.value || !manualData.value) {
    alert("Please fill out all fields."); return;
  }
  
  const columns = manualColumns.value.split(',').map(c => c.trim());
  const rows = manualData.value.split('\n').filter(line => line.trim() !== '').map(line => {
    const vals = line.split(',');
    let obj = {};
    columns.forEach((col, idx) => {
      obj[col] = vals[idx] ? vals[idx].trim() : '';
    });
    return obj;
  });

  try {
    const token = await authStore.user.getIdToken();
    const res = await fetch('http://localhost:8000/api/datasets/create', {
      method: 'POST',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name: manualName.value, rows })
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    alert(`Successfully created dataset "${manualName.value}" with ${data.row_count} rows!`);
    showModal.value = false;
    manualName.value = '';
    manualColumns.value = '';
    manualData.value = '';
  } catch (err) {
    alert("Error creating dataset: " + err.message);
  }
};
</script>

<style scoped>
.mt-4 { margin-top: 2rem; }
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
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
  max-width: 600px;
}
</style>
