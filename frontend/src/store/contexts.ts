import { create } from "zustand";
import { Context } from "@/types";
import { contextAPI } from "@/services/api";

interface ContextState {
  contexts: Record<string, Context>;
  currentContext: Context | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
  
  // Actions
  fetchContext: (meetingId: string) => Promise<void>;
  generateContext: (meetingId: string, forceRegenerate?: boolean) => Promise<Context | null>;
  updateContext: (contextId: string, data: any) => Promise<void>;
  deleteContext: (contextId: string) => Promise<void>;
  fetchRecentContexts: (limit?: number) => Promise<void>;
  setCurrentContext: (context: Context | null) => void;
  setError: (error: string | null) => void;
}

export const useContextStore = create<ContextState>((set, get) => ({
  contexts: {},
  currentContext: null,
  isLoading: false,
  isGenerating: false,
  error: null,

  fetchContext: async (meetingId: string) => {
    try {
      set({ isLoading: true, error: null });
      const context = await contextAPI.getByMeeting(meetingId);
      set({ 
        contexts: { ...get().contexts, [meetingId]: context },
        currentContext: context,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to fetch context",
        isLoading: false 
      });
    }
  },

  generateContext: async (meetingId: string, forceRegenerate = false) => {
    try {
      set({ isGenerating: true, error: null });
      const context = await contextAPI.generate(meetingId, forceRegenerate);
      set({ 
        contexts: { ...get().contexts, [meetingId]: context },
        currentContext: context,
        isGenerating: false 
      });
      return context;
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to generate context",
        isGenerating: false 
      });
      return null;
    }
  },

  updateContext: async (contextId: string, data: any) => {
    try {
      set({ isLoading: true, error: null });
      const updated = await contextAPI.update(contextId, data);
      const meetingId = updated.meeting_id;
      set({ 
        contexts: { ...get().contexts, [meetingId]: updated },
        currentContext: updated,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to update context",
        isLoading: false 
      });
    }
  },

  deleteContext: async (contextId: string) => {
    try {
      set({ isLoading: true, error: null });
      await contextAPI.delete(contextId);
      const newContexts = { ...get().contexts };
      const meetingId = Object.keys(newContexts).find(
        key => newContexts[key].id === contextId
      );
      if (meetingId) {
        delete newContexts[meetingId];
      }
      set({ contexts: newContexts, currentContext: null, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to delete context",
        isLoading: false 
      });
    }
  },

  fetchRecentContexts: async (limit = 10) => {
    try {
      set({ isLoading: true, error: null });
      const contexts = await contextAPI.recent(limit);
      const contextMap: Record<string, Context> = {};
      contexts.forEach((ctx: Context) => {
        contextMap[ctx.meeting_id] = ctx;
      });
      set({ contexts: { ...get().contexts, ...contextMap }, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to fetch recent contexts",
        isLoading: false 
      });
    }
  },

  setCurrentContext: (context: Context | null) => {
    set({ currentContext: context });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));
