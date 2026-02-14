import axios, { AxiosInstance, AxiosError } from "axios";
import { AuthToken } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_TIMEOUT = parseInt(process.env.NEXT_PUBLIC_API_TIMEOUT || "30000");

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      timeout: API_TIMEOUT,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Load token from localStorage on initialization
    this.token =
      typeof window !== "undefined" ? localStorage.getItem("auth_token") : null;

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          this.logout();
        }
        return Promise.reject(error);
      },
    );
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem("auth_token", token);
  }

  getToken(): string | null {
    if (!this.token) {
      this.token = localStorage.getItem("auth_token");
    }
    return this.token;
  }

  logout() {
    this.token = null;
    localStorage.removeItem("auth_token");
  }

  async request(method: string, url: string, data?: any) {
    try {
      const response = await this.client.request({
        method,
        url,
        data,
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  get(url: string) {
    return this.request("GET", url);
  }

  post(url: string, data: any) {
    return this.request("POST", url, data);
  }

  put(url: string, data: any) {
    return this.request("PUT", url, data);
  }

  delete(url: string) {
    return this.request("DELETE", url);
  }
}

export const apiClient = new APIClient();

// ============================================
// Authentication API
// ============================================
export const authAPI = {
  register: (data: { email: string; name: string; password: string }) =>
    apiClient.post("/auth/register", data),

  login: (data: { email: string; password: string }) =>
    apiClient.post("/auth/login", data),

  me: () => apiClient.get("/auth/me"),

  googleCallback: (code: string, redirectUri: string) =>
    apiClient.post("/auth/google/callback", {
      code,
      redirect_uri: redirectUri,
    }),

  refresh: () => apiClient.post("/auth/refresh", {}),

  logout: () => apiClient.delete("/auth/logout"),
};

// ============================================
// Meetings API
// ============================================
export const meetingsAPI = {
  list: (params?: {
    skip?: number;
    limit?: number;
    search?: string;
    status?: string;
  }) => {
    const queryString = params
      ? "?" + new URLSearchParams(params as any).toString()
      : "";
    return apiClient.get(`/meetings${queryString}`);
  },

  get: (id: string) => apiClient.get(`/meetings/${id}`),

  create: (data: {
    title: string;
    description?: string;
    start_time: string;
    end_time: string;
    attendees: string[];
    meeting_link?: string;
    location?: string;
  }) => apiClient.post("/meetings", data),

  update: (id: string, data: any) => apiClient.put(`/meetings/${id}`, data),

  delete: (id: string) => apiClient.delete(`/meetings/${id}`),

  syncGoogle: () => apiClient.post("/meetings/sync/google", {}),

  todayUpcoming: () => apiClient.get("/meetings/today/upcoming"),

  stats: () => apiClient.get("/meetings/stats/overview"),
};

// ============================================
// Context API
// ============================================
export const contextAPI = {
  getByMeeting: (meetingId: string) =>
    apiClient.get(`/contexts/meeting/${meetingId}`),

  generate: (meetingId: string, forceRegenerate: boolean = false) =>
    apiClient.post(
      `/contexts/generate/${meetingId}?force_regenerate=${forceRegenerate}`,
      {},
    ),

  update: (contextId: string, data: any) =>
    apiClient.put(`/contexts/${contextId}`, data),

  delete: (contextId: string) => apiClient.delete(`/contexts/${contextId}`),

  recent: (limit: number = 10) =>
    apiClient.get(`/contexts/user/recent?limit=${limit}`),

  batchGenerate: (meetingIds: string[]) =>
    apiClient.post("/contexts/batch/generate", { meeting_ids: meetingIds }),
};

// ============================================
// Notifications API
// ============================================
export const notificationsAPI = {
  list: (params?: { status?: string; skip?: number; limit?: number }) =>
    apiClient.get(`/notifications?${new URLSearchParams(params as any)}`),

  schedule: (data: {
    meeting_id: string;
    channel: string;
    scheduled_time: string;
  }) => apiClient.post("/notifications/schedule", data),

  autoSchedule: (meetingId: string) =>
    apiClient.post(`/notifications/meeting/${meetingId}/auto-schedule`, {}),

  cancel: (id: string) => apiClient.delete(`/notifications/${id}`),

  pending: () => apiClient.get("/notifications/pending/upcoming"),

  resend: (id: string) => apiClient.post(`/notifications/${id}/resend`, {}),

  stats: () => apiClient.get("/notifications/stats/overview"),
};
