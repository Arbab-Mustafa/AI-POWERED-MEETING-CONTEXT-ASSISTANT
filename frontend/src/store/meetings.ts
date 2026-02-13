import { create } from "zustand";
import { Meeting } from "@/types";
import { meetingsAPI } from "@/services/api";

interface MeetingState {
  meetings: Meeting[];
  currentMeeting: Meeting | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  fetchMeetings: (params?: any) => Promise<void>;
  fetchMeeting: (id: string) => Promise<void>;
  createMeeting: (data: any) => Promise<Meeting | null>;
  updateMeeting: (id: string, data: any) => Promise<void>;
  deleteMeeting: (id: string) => Promise<void>;
  syncGoogleCalendar: () => Promise<void>;
  fetchTodayMeetings: () => Promise<void>;
  setCurrentMeeting: (meeting: Meeting | null) => void;
  setError: (error: string | null) => void;
}

export const useMeetingStore = create<MeetingState>((set, get) => ({
  meetings: [],
  currentMeeting: null,
  isLoading: false,
  error: null,

  fetchMeetings: async (params?: any) => {
    try {
      set({ isLoading: true, error: null });
      const data = await meetingsAPI.list(params);
      set({ meetings: data.meetings || data, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to fetch meetings",
        isLoading: false 
      });
    }
  },

  fetchMeeting: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      const meeting = await meetingsAPI.get(id);
      set({ currentMeeting: meeting, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to fetch meeting",
        isLoading: false 
      });
    }
  },

  createMeeting: async (data: any) => {
    try {
      set({ isLoading: true, error: null });
      const meeting = await meetingsAPI.create(data);
      set({ 
        meetings: [...get().meetings, meeting],
        currentMeeting: meeting,
        isLoading: false 
      });
      return meeting;
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to create meeting",
        isLoading: false 
      });
      return null;
    }
  },

  updateMeeting: async (id: string, data: any) => {
    try {
      set({ isLoading: true, error: null });
      const updated = await meetingsAPI.update(id, data);
      set({ 
        meetings: get().meetings.map(m => m.id === id ? updated : m),
        currentMeeting: updated,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to update meeting",
        isLoading: false 
      });
    }
  },

  deleteMeeting: async (id: string) => {
    try {
      set({ isLoading: true, error: null });
      await meetingsAPI.delete(id);
      set({ 
        meetings: get().meetings.filter(m => m.id !== id),
        currentMeeting: null,
        isLoading: false 
      });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to delete meeting",
        isLoading: false 
      });
    }
  },

  syncGoogleCalendar: async () => {
    try {
      set({ isLoading: true, error: null });
      const result = await meetingsAPI.syncGoogle();
      await get().fetchMeetings();
      set({ isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to sync Google Calendar",
        isLoading: false 
      });
    }
  },

  fetchTodayMeetings: async () => {
    try {
      set({ isLoading: true, error: null });
      const meetings = await meetingsAPI.todayUpcoming();
      set({ meetings, isLoading: false });
    } catch (error: any) {
      set({ 
        error: error.response?.data?.detail || "Failed to fetch today's meetings",
        isLoading: false 
      });
    }
  },

  setCurrentMeeting: (meeting: Meeting | null) => {
    set({ currentMeeting: meeting });
  },

  setError: (error: string | null) => {
    set({ error });
  },
}));
