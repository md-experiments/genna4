import { defineStore } from 'pinia';

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    // Keys are kept in memory only (not localstorage) to ensure they are never stored on disk
    openaiKey: '',
    anthropicKey: '',
    openrouterKey: ''
  })
});
