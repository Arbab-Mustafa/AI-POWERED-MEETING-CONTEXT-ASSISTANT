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
