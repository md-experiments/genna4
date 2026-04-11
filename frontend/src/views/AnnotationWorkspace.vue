<template>
  <div class="workspace">
    <div class="card toolbar" style="margin-bottom: 1.5rem; display: flex; justify-content: space-between;">
      <div class="filters">
        <input type="text" placeholder="Search by content..." class="input-field" style="width: 250px; margin-bottom: 0;" />
        <label style="margin-left: 1rem;">
          <input type="checkbox" v-model="showOnlyDisagreements" />
          Show only AI disagreements
        </label>
      </div>
      <div class="actions">
        <button @click="toggleHideAllAnnotations">{{ hideAnnotations ? 'Show Annotations' : 'Hide Annotations' }}</button>
      </div>
    </div>

    <!-- Main Dataset Table / List -->
    <div class="dataset-list">
      <div class="card dataset-row" v-for="row in dummyRows" :key="row.id" style="margin-bottom: 1rem;">
        <div class="row-header" style="display: flex; justify-content: space-between; margin-bottom: 1rem;">
          <h3 style="font-size: 1.1rem;">Row ID: {{ row.id }}</h3>
          <span v-if="row.hasDisagreement" class="badge danger">Disagreement Detected</span>
          <span v-else class="badge success">Agreement</span>
        </div>
        
        <div class="row-content" style="padding: 1rem; background-color: var(--bg-color); border-radius: 4px; border: 1px solid var(--border-color); margin-bottom: 1rem;">
          {{ row.content }}
        </div>

        <div v-if="!hideAnnotations" class="annotations-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
          <!-- Model Outputs -->
          <div class="annotation-card" v-for="model in row.models" :key="model.name" style="border: 1px solid var(--border-color); border-radius: 4px; padding: 1rem;">
            <div style="font-weight: 600; margin-bottom: 0.5rem; display: flex; justify-content: space-between;">
              {{ model.name }}
              <div class="feedback-actions">
                <button class="icon-btn">👍</button>
                <button class="icon-btn">👎</button>
              </div>
            </div>
            <div class="output-text" style="font-size: 0.9rem; color: var(--text-color-secondary);">
              {{ model.output }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const showOnlyDisagreements = ref(false);
const hideAnnotations = ref(false);

const toggleHideAllAnnotations = () => {
  hideAnnotations.value = !hideAnnotations.value;
};

// Dummy Data for testing aesthetics
const dummyRows = ref([
  {
    id: "r_123",
    content: "The company reported a sequential revenue growth of 15% Q/Q, driven primarily by the enterprise segment.",
    hasDisagreement: true,
    models: [
      { name: "OpenRouter (Claude 3 Haiku)", output: "Category: Finance, Positive Sentiment" },
      { name: "OpenAI (GPT-4o)", output: "Category: Technology, Positive Sentiment" },
    ]
  },
  {
    id: "r_124",
    content: "Initial public offering (IPO) expected next fiscal year depends entirely on macroeconomic stability.",
    hasDisagreement: false,
    models: [
      { name: "OpenRouter (Claude 3 Haiku)", output: "Category: Finance, Neutral Sentiment" },
      { name: "OpenAI (GPT-4o)", output: "Category: Finance, Neutral Sentiment" },
    ]
  }
]);
</script>

<style scoped>
.toolbar {
  align-items: center;
}
.badge {
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.8rem;
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
[data-theme='dark'] .badge.danger {
  background-color: rgba(244, 67, 54, 0.1);
}
[data-theme='dark'] .badge.success {
  background-color: rgba(76, 175, 80, 0.1);
}
.icon-btn {
  background: none;
  border: none;
  color: var(--text-color);
  padding: 0.25rem;
  cursor: pointer;
  opacity: 0.7;
}
.icon-btn:hover {
  opacity: 1;
  background-color: var(--bg-color-secondary);
}
</style>
