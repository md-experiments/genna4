import { defineStore } from 'pinia';
import { auth } from '../firebase';
import { signInWithEmailAndPassword, signOut, onAuthStateChanged } from 'firebase/auth';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: true,
  }),
  actions: {
    async init() {
      return new Promise((resolve) => {
        onAuthStateChanged(auth, (user) => {
          this.user = user;
          this.loading = false;
          resolve();
        });
      });
    },
    async login(email, password) {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      this.user = userCredential.user;
    },
    async logout() {
      await signOut(auth);
      this.user = null;
    }
  }
});
