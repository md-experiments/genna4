<template>
  <div class="workspace">
    <!-- ── Back button ──────────────────────────────────────────────────── -->
    <div style="margin-bottom: 1rem;">
      <button @click="router.push('/')" style="background: transparent; color: var(--text-color); border: 1px solid var(--border-color);">
        ← Back to Datasets
      </button>
    </div>

    <!-- ── Model Configuration Panel ──────────────────────────────────── -->
    <div class="card" style="margin-bottom: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
        <h3 style="margin: 0;">Model Configuration</h3>
        <div style="display: flex; gap: 0.5rem;">
          <button @click="modelConfigsStore.addConfig()" style="font-size: 0.85rem;">+ Add Model</button>
          <button @click="runAnnotation" :disabled="running" style="font-size: 0.85rem;">
            {{ running ? 'Running…' : 'Run Annotation' }}
          </button>
        </div>
      </div>

      <div class="model-configs-grid">
        <div
          v-for="cfg in modelConfigsStore.configs"
          :key="cfg.id"
          class="model-config-card"
        >
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
            <strong style="font-size: 0.9rem;">Model Slot</strong>
            <button
              v-if="modelConfigsStore.configs.length > 1"
              @click="modelConfigsStore.removeConfig(cfg.id)"
              style="background: none; border: none; color: var(--danger-color); cursor: pointer; font-size: 0.9rem;"
            >✕</button>
          </div>

          <label class="cfg-label">Provider</label>
          <select v-model="cfg.provider" class="input-field cfg-select">
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="openrouter">OpenRouter</option>
          </select>

          <label class="cfg-label">Model Name</label>
          <input v-model="cfg.model" class="input-field" placeholder="e.g. gpt-4o" />

          <label class="cfg-label">System Prompt</label>
          <textarea v-model="cfg.systemPrompt" class="input-field" rows="2" placeholder="Optional system prompt…" style="resize: vertical;"></textarea>

          <div style="display: flex; gap: 1rem; margin-top: 0.25rem;">
            <div style="flex: 1;">
              <label class="cfg-label">Temp: {{ cfg.temperature.toFixed(1) }}</label>
              <input type="range" v-model.number="cfg.temperature" min="0" max="2" step="0.1" style="width: 100%;" />
            </div>
            <div style="flex: 1;">
              <label class="cfg-label">Max Tokens</label>
              <input type="number" v-model.number="cfg.maxTokens" class="input-field" min="64" max="4096" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Toolbar ─────────────────────────────────────────────────────── -->
    <div class="card toolbar" style="margin-bottom: 1.5rem;">
      <div class="filters" style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap;">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search by content…"
          class="input-field"
          style="width: 220px; margin-bottom: 0;"
        />
        <label style="display: flex; align-items: center; gap: 0.4rem; white-space: nowrap;">
          <input type="checkbox" v-model="showOnlyDisagreements" />
          Disagreements only
        </label>

        <!-- Category filter chips -->
        <div v-if="availableCategories.length > 0" style="display: flex; gap: 0.4rem; flex-wrap: wrap; align-items: center;">
          <span style="font-size: 0.8rem; color: var(--text-color-secondary);">Category:</span>
          <button
            v-for="cat in availableCategories"
            :key="cat"
            @click="toggleCategory(cat)"
            class="cat-chip"
            :class="{ active: selectedCategories.has(cat) }"
          >{{ cat }}</button>
        </div>
      </div>

      <div class="actions" style="display: flex; gap: 0.5rem;">
        <button @click="hideAnnotations = !hideAnnotations">
          {{ hideAnnotations ? 'Show Annotations' : 'Hide Annotations' }}
        </button>
      </div>
    </div>

    <!-- ── Status / progress ───────────────────────────────────────────── -->
    <div v-if="loadingRows" class="card" style="margin-bottom: 1rem; color: var(--text-color-secondary);">
      Loading rows…
    </div>
    <div v-else-if="running" class="card" style="margin-bottom: 1rem; color: var(--text-color-secondary);">
      Running inference ({{ annotatedCount }}/{{ rows.length }} rows done)…
    </div>

    <!-- ── Dataset rows ────────────────────────────────────────────────── -->
    <div class="dataset-list">
      <div
        class="card dataset-row"
        v-for="row in filteredRows"
        :key="row._rowKey"
        style="margin-bottom: 1rem;"
      >
        <!-- Row header -->
        <div class="row-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <div style="display: flex; align-items: center; gap: 0.75rem;">
            <button class="expand-btn" @click="toggleExpand(row._rowKey)">
              {{ expandedRows.has(row._rowKey) ? '▼' : '▶' }}
            </button>
            <span style="font-size: 0.85rem; color: var(--text-color-secondary);">
              Row {{ row.id || row._rowKey }}
            </span>
          </div>
          <span
            v-if="row._annotations.length > 0"
            class="badge"
            :class="row._disagreement.has_disagreement ? 'danger' : 'success'"
          >
            {{ row._disagreement.has_disagreement ? 'Disagreement' : 'Agreement' }}
            <span v-if="row._disagreement.score > 0" style="margin-left: 0.25rem; opacity: 0.8;">
              ({{ Math.round(row._disagreement.score * 100) }}%)
            </span>
          </span>
          <span v-else-if="running" class="badge neutral">Pending…</span>
        </div>

        <!-- Row content (always visible) -->
        <div class="row-content" style="padding: 0.75rem; background-color: var(--bg-color); border-radius: 4px; border: 1px solid var(--border-color); margin-bottom: 0.75rem; font-size: 0.92rem;">
          {{ row[promptColumn] || JSON.stringify(row, null, 2) }}
        </div>

        <!-- Expanded: all columns as key/value -->
        <div v-if="expandedRows.has(row._rowKey)" style="margin-bottom: 0.75rem;">
          <div
            v-for="(val, key) in rowDisplayFields(row)"
            :key="key"
            style="display: flex; gap: 0.5rem; font-size: 0.82rem; border-bottom: 1px solid var(--border-color); padding: 0.3rem 0;"
          >
            <span style="color: var(--text-color-secondary); min-width: 120px; font-weight: 600;">{{ key }}</span>
            <span>{{ val }}</span>
          </div>
        </div>

        <!-- Model outputs -->
        <div v-if="!hideAnnotations && row._annotations.length > 0" class="annotations-grid">
          <div
            class="annotation-card"
            v-for="ann in row._annotations"
            :key="ann.annotationId || ann.modelLabel"
          >
            <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem;">
              <span>{{ ann.modelLabel }}</span>
              <div class="feedback-actions">
                <button
                  class="icon-btn"
                  :class="{ active: ann.thumbs === true }"
                  @click="submitThumb(row, ann, true)"
                  title="Thumbs up"
                >👍</button>
                <button
                  class="icon-btn"
                  :class="{ active: ann.thumbs === false }"
                  @click="submitThumb(row, ann, false)"
                  title="Thumbs down"
                >👎</button>
              </div>
            </div>
            <div class="output-text" style="font-size: 0.88rem; color: var(--text-color-secondary); white-space: pre-wrap;">
              {{ ann.output }}
            </div>
          </div>
        </div>
      </div>

      <div v-if="!loadingRows && filteredRows.length === 0 && rows.length > 0" style="color: var(--text-color-secondary); text-align: center; padding: 2rem;">
        No rows match the current filters.
      </div>
      <div v-if="!loadingRows && rows.length === 0" style="color: var(--text-color-secondary); text-align: center; padding: 2rem;">
        This dataset has no rows.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useSettingsStore } from '../stores/settings';
import { useModelConfigsStore } from '../stores/modelConfigs';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const settingsStore = useSettingsStore();
const modelConfigsStore = useModelConfigsStore();

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const datasetId = route.params.datasetId;

// ── State ───────────────────────────────────────────────────────────────────

const rows = ref([]);           // raw rows from Firestore (with _annotations/_disagreement injected)
const loadingRows = ref(true);
const running = ref(false);
const annotatedCount = ref(0);

// Filtering
const searchQuery = ref('');
const showOnlyDisagreements = ref(false);
const selectedCategories = ref(new Set());
const hideAnnotations = ref(false);
const expandedRows = ref(new Set());

// The column whose value is used as the user prompt
const promptColumn = ref('content');

// ── Helpers ─────────────────────────────────────────────────────────────────

async function getToken() {
  return authStore.user.getIdToken();
}

function apiHeaders(token) {
  const h = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json',
  };
  if (settingsStore.openaiKey)     h['x-openai-key']     = settingsStore.openaiKey;
  if (settingsStore.anthropicKey)  h['x-anthropic-key']  = settingsStore.anthropicKey;
  if (settingsStore.openrouterKey) h['x-openrouter-key'] = settingsStore.openrouterKey;
  return h;
}

function rowDisplayFields(row) {
  const skip = new Set(['_rowKey', '_annotations', '_disagreement']);
  return Object.fromEntries(Object.entries(row).filter(([k]) => !skip.has(k)));
}

// ── Load rows ────────────────────────────────────────────────────────────────

async function fetchRows() {
  loadingRows.value = true;
  try {
    const token = await getToken();
    const res = await fetch(`${API_BASE}/api/datasets/${datasetId}/rows`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();

    // Detect prompt column from first row keys
    const firstRow = data.rows[0] || {};
    const candidates = ['content', 'text', 'prompt', 'input', 'sentence'];
    promptColumn.value = candidates.find((c) => c in firstRow) || Object.keys(firstRow)[0] || 'content';

    rows.value = (data.rows || []).map((r, i) => ({
      ...r,
      _rowKey: r.id || String(i),
      _annotations: [],
      _disagreement: { has_disagreement: false, score: 0 },
    }));
  } catch (err) {
    console.error('Failed to load rows:', err);
  } finally {
    loadingRows.value = false;
  }
}

// ── Run annotation (batch inference) ────────────────────────────────────────

async function runAnnotation() {
  if (modelConfigsStore.configs.length === 0) {
    alert('Add at least one model configuration first.');
    return;
  }
  const configs = modelConfigsStore.configs;
  const missingModel = configs.find((c) => !c.model.trim());
  if (missingModel) {
    alert('Please enter a model name for all model slots.');
    return;
  }

  running.value = true;
  annotatedCount.value = 0;

  try {
    const token = await getToken();

    // Process rows in chunks of 10 to avoid overwhelming the server
    const chunkSize = 10;
    for (let i = 0; i < rows.value.length; i += chunkSize) {
      const chunk = rows.value.slice(i, i + chunkSize);

      const res = await fetch(`${API_BASE}/api/inference/batch`, {
        method: 'POST',
        headers: apiHeaders(token),
        body: JSON.stringify({
          models: configs.map((c) => ({
            provider: c.provider,
            model: c.model,
            system: c.systemPrompt || null,
            temperature: c.temperature,
            max_tokens: c.maxTokens,
          })),
          rows: chunk.map((r) => rowDisplayFields(r)),
          prompt_column: promptColumn.value,
        }),
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();

      data.results.forEach((result, idx) => {
        const rowIndex = i + idx;
        rows.value[rowIndex]._annotations = result.model_outputs.map((mo) => ({
          modelLabel: `${mo.provider} / ${mo.model}`,
          output: mo.output,
          thumbs: null,
          annotationId: null,
        }));
        rows.value[rowIndex]._disagreement = result.disagreement;
      });

      annotatedCount.value += chunk.length;
    }

    // Persist annotations to backend
    await persistAnnotations(token);
  } catch (err) {
    alert('Inference error: ' + err.message);
  } finally {
    running.value = false;
  }
}

async function persistAnnotations(token) {
  for (const row of rows.value) {
    for (const ann of row._annotations) {
      if (ann.annotationId) continue; // already saved
      try {
        const res = await fetch(`${API_BASE}/api/annotations/`, {
          method: 'POST',
          headers: apiHeaders(token),
          body: JSON.stringify({
            dataset_id: datasetId,
            row_id: row._rowKey,
            model_config_id: ann.modelLabel,
            response_text: ann.output,
          }),
        });
        if (res.ok) {
          const saved = await res.json();
          ann.annotationId = saved.annotation.id;
        }
      } catch (e) {
        console.warn('Failed to persist annotation:', e);
      }
    }
  }
}

// ── Thumbs feedback ──────────────────────────────────────────────────────────

async function submitThumb(row, ann, value) {
  ann.thumbs = value;
  if (!ann.annotationId) return; // not yet persisted

  try {
    const token = await getToken();
    await fetch(`${API_BASE}/api/annotations/${datasetId}/${ann.annotationId}`, {
      method: 'PATCH',
      headers: apiHeaders(token),
      body: JSON.stringify({ thumbs_up: value }),
    });
  } catch (e) {
    console.warn('Failed to save thumb:', e);
  }
}

// ── Expand / collapse ────────────────────────────────────────────────────────

function toggleExpand(rowKey) {
  if (expandedRows.value.has(rowKey)) {
    expandedRows.value.delete(rowKey);
  } else {
    expandedRows.value.add(rowKey);
  }
}

// ── Category filter ───────────────────────────────────────────────────────────

const categoryColumn = computed(() => {
  const candidates = ['category', 'label', 'class', 'type'];
  const firstRow = rows.value[0] || {};
  return candidates.find((c) => c in firstRow) || null;
});

const availableCategories = computed(() => {
  if (!categoryColumn.value) return [];
  const vals = new Set(rows.value.map((r) => r[categoryColumn.value]).filter(Boolean));
  return [...vals].sort();
});

function toggleCategory(cat) {
  const s = new Set(selectedCategories.value);
  if (s.has(cat)) {
    s.delete(cat);
  } else {
    s.add(cat);
  }
  selectedCategories.value = s;
}

// ── Filtered rows ─────────────────────────────────────────────────────────────

const filteredRows = computed(() => {
  let result = rows.value;

  if (showOnlyDisagreements.value) {
    result = result.filter((r) => r._disagreement.has_disagreement);
  }

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase();
    result = result.filter((r) => {
      return Object.entries(rowDisplayFields(r)).some(([, v]) =>
        String(v).toLowerCase().includes(q)
      );
    });
  }

  if (selectedCategories.value.size > 0 && categoryColumn.value) {
    result = result.filter((r) => selectedCategories.value.has(r[categoryColumn.value]));
  }

  return result;
});

const annotatedCount_display = computed(() =>
  rows.value.filter((r) => r._annotations.length > 0).length
);

onMounted(fetchRows);
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 9999px;
  font-size: 0.78rem;
  font-weight: 600;
}
.badge.danger {
  background-color: #ffebee;
  color: var(--danger-color);
  border: 1px solid var(--danger-color);
}
.badge.success {
  background-color: #e8f5e9;
  color: var(--success-color);
  border: 1px solid var(--success-color);
}
.badge.neutral {
  background-color: var(--bg-color-secondary);
  color: var(--text-color-secondary);
  border: 1px solid var(--border-color);
}
[data-theme='dark'] .badge.danger  { background-color: rgba(244, 67, 54, 0.1); }
[data-theme='dark'] .badge.success { background-color: rgba(76, 175, 80, 0.1); }

.annotations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}
.annotation-card {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.85rem;
}
.icon-btn {
  background: none;
  border: none;
  color: var(--text-color);
  padding: 0.2rem 0.3rem;
  cursor: pointer;
  opacity: 0.5;
  border-radius: 4px;
  font-size: 1rem;
  transition: opacity 0.1s, background-color 0.1s;
}
.icon-btn:hover  { opacity: 0.9; background-color: var(--bg-color-secondary); }
.icon-btn.active { opacity: 1; background-color: var(--bg-color-secondary); }

.expand-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-color-secondary);
  font-size: 0.7rem;
  padding: 0.2rem;
}

.model-configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}
.model-config-card {
  border: 1px solid var(--border-color);
  border-radius: 4px;
  padding: 0.85rem;
}
.cfg-label {
  display: block;
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.2rem;
  color: var(--text-color-secondary);
}
.cfg-select {
  margin-bottom: 0.5rem;
}

.cat-chip {
  font-size: 0.75rem;
  padding: 0.15rem 0.5rem;
  border-radius: 9999px;
  border: 1px solid var(--border-color);
  background: none;
  cursor: pointer;
  color: var(--text-color);
  transition: background-color 0.1s;
}
.cat-chip:hover  { background-color: var(--bg-color-secondary); }
.cat-chip.active {
  background-color: var(--primary-color, #1a73e8);
  color: #fff;
  border-color: var(--primary-color, #1a73e8);
}
</style>
