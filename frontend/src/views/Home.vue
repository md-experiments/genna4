<template>
  <div class="dashboard">
    <div class="card mt-4">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h2>Datasets</h2>
        <button @click="showModal = true">New Dataset</button>
      </div>

      <div v-if="loadingDatasets" style="color: var(--text-color-secondary);">Loading datasets…</div>
      <div v-else-if="datasets.length === 0" style="color: var(--text-color-secondary);">
        No datasets found. Create or upload one to get started.
      </div>
      <div v-else class="dataset-grid">
        <div
          v-for="ds in datasets"
          :key="ds.id"
          class="dataset-card card"
          @click="openDataset(ds.id)"
        >
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div class="dataset-name">{{ ds.name }}</div>
              <div class="dataset-meta">{{ ds.row_count }} rows · {{ formatDate(ds.created_at) }}</div>
            </div>
            <button
              class="btn-danger-sm"
              @click.stop="confirmDelete(ds)"
              title="Delete dataset"
            >✕</button>
          </div>
        </div>
      </div>
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
          <button @click="triggerFileInput" style="width: 100%;" :disabled="uploading">
            {{ uploading ? 'Uploading…' : 'Select & Upload File' }}
          </button>
        </div>

        <!-- Manual Entry Tab -->
        <div v-if="tab === 'manual'">
          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Dataset Name</label>
          <input type="text" v-model="manualName" placeholder="My Dataset" class="input-field" />

          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Columns (comma separated)</label>
          <input type="text" v-model="manualColumns" placeholder="id, content, label" class="input-field" />

          <label style="display:block; margin-bottom: 0.25rem; font-weight: 600;">Data (one row per line, comma separated)</label>
          <textarea v-model="manualData" rows="6" class="input-field" placeholder="1, The stock market crashed, Finance&#10;2, The new iPhone is great, Tech" style="resize: vertical; font-family: monospace;"></textarea>

          <button @click="submitManualDataset" style="width: 100%;" :disabled="uploading">
            {{ uploading ? 'Creating…' : 'Create Dataset' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const router = useRouter();

// Empty string → same-origin proxy (production); undefined → local dev default
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

const datasets = ref([]);
const loadingDatasets = ref(true);
const showModal = ref(false);
const tab = ref('upload');
const uploading = ref(false);

const fileInput = ref(null);
const manualName = ref('');
const manualColumns = ref('');
const manualData = ref('');

async function getToken() {
  return authStore.user.getIdToken();
}

async function fetchDatasets() {
  loadingDatasets.value = true;
  try {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/datasets/`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    datasets.value = data.datasets || [];
  } catch (err) {
    console.error('Failed to load datasets:', err);
  } finally {
    loadingDatasets.value = false;
  }
}

function openDataset(datasetId) {
  router.push(`/workspace/${datasetId}`);
}

function formatDate(iso) {
  if (!iso) return '';
  return new Date(iso).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

async function confirmDelete(ds) {
  if (!confirm(`Delete dataset "${ds.name}"? This cannot be undone.`)) return;
  try {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/datasets/${ds.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(await res.text());
    datasets.value = datasets.value.filter((d) => d.id !== ds.id);
  } catch (err) {
    alert('Error deleting dataset: ' + err.message);
  }
}

const triggerFileInput = () => {
  if (fileInput.value) fileInput.value.click();
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  uploading.value = true;
  try {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/datasets/upload`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    alert(`Successfully uploaded ${data.row_count} rows!`);
    showModal.value = false;
    await fetchDatasets();
  } catch (err) {
    alert('Error uploading dataset: ' + err.message);
  } finally {
    uploading.value = false;
    if (fileInput.value) fileInput.value.value = '';
  }
};

const submitManualDataset = async () => {
  if (!manualName.value || !manualColumns.value || !manualData.value) {
    alert('Please fill out all fields.');
    return;
  }
  const columns = manualColumns.value.split(',').map((c) => c.trim());
  const rows = manualData.value
    .split('\n')
    .filter((line) => line.trim() !== '')
    .map((line) => {
      const vals = line.split(',');
      const obj = {};
      columns.forEach((col, idx) => {
        obj[col] = vals[idx] ? vals[idx].trim() : '';
      });
      return obj;
    });

  uploading.value = true;
  try {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/datasets/create`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name: manualName.value, rows }),
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    alert(`Successfully created dataset "${manualName.value}" with ${data.row_count} rows!`);
    showModal.value = false;
    manualName.value = '';
    manualColumns.value = '';
    manualData.value = '';
    await fetchDatasets();
  } catch (err) {
    alert('Error creating dataset: ' + err.message);
  } finally {
    uploading.value = false;
  }
};

onMounted(fetchDatasets);
</script>

<style scoped>
.mt-4 { margin-top: 2rem; }
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.dataset-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}
.dataset-card {
  cursor: pointer;
  transition: box-shadow 0.15s;
  padding: 1rem 1.25rem;
}
.dataset-card:hover {
  box-shadow: 0 2px 12px rgba(0,0,0,0.12);
}
.dataset-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.25rem;
}
.dataset-meta {
  font-size: 0.8rem;
  color: var(--text-color-secondary);
}
.btn-danger-sm {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  font-size: 0.85rem;
  padding: 0.1rem 0.35rem;
  border-radius: 4px;
  opacity: 0.7;
}
.btn-danger-sm:hover {
  opacity: 1;
  background-color: rgba(244,67,54,0.1);
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
