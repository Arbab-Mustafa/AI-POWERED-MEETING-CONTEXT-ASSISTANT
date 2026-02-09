import { create } from "zustand";
import { User, AuthToken } from "@/types";
import { apiClient } from "@/services/api";

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  restoreSession: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  setUser: (user: User) => {
    set({ user, isAuthenticated: true });
  },

  setToken: (token: string) => {
    apiClient.setToken(token);
  },

  logout: () => {
    apiClient.logout();
    set({
      user: null,
      isAuthenticated: false,
      error: null,
    });
  },

  setError: (error: string | null) => {
    set({ error });
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  restoreSession: async () => {
    try {
      set({ isLoading: true });
      const token = apiClient.getToken();
      if (!token) {
        set({ isLoading: false });
        return;
      }
    } catch (error) {
      set({ error: "Session restore failed" });
    } finally {
      set({ isLoading: false });
    }
  },
}));
