import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useModelConfigsStore = defineStore('modelConfigs', () => {
  // Each config: { id, provider, model, systemPrompt, temperature, maxTokens }
  const configs = ref([
    {
      id: 'default-1',
      provider: 'openai',
      model: 'gpt-4o',
      systemPrompt: '',
      temperature: 0.7,
      maxTokens: 1024,
    },
  ]);

  function addConfig() {
    configs.value.push({
      id: crypto.randomUUID(),
      provider: 'openai',
      model: '',
      systemPrompt: '',
      temperature: 0.7,
      maxTokens: 1024,
    });
  }

  function removeConfig(id) {
    configs.value = configs.value.filter((c) => c.id !== id);
  }

  return { configs, addConfig, removeConfig };
});
