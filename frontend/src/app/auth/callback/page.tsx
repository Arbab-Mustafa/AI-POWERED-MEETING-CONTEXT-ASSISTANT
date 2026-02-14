"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { authAPI } from "@/services/api";

export default function GoogleCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser, setToken, setError } = useAuthStore();
  const [status, setStatus] = useState<"loading" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const hasRun = useRef(false); // Prevent double execution

  useEffect(() => {
    // Prevent double execution in development (React StrictMode)
    if (hasRun.current) return;
    hasRun.current = true;
    
    const handleCallback = async () => {
      const code = searchParams.get("code");
      const error = searchParams.get("error");

      if (error) {
        setErrorMessage(`Google authentication failed: ${error}`);
        setStatus("error");
        return;
      }

      if (!code) {
        setErrorMessage("No authorization code received");
        setStatus("error");
        return;
      }

      try {
        // Exchange code for token with the same redirect_uri used in initial request
        const redirectUri = `${window.location.origin}/auth/callback`;
        const response = await authAPI.googleCallback(code, redirectUri);
        
        // Save auth data
        setToken(response.access_token);
        setUser(response.user);
        
        // Redirect to dashboard
        router.push("/dashboard");
      } catch (err: any) {
        console.error("Google OAuth error:", err);
        setErrorMessage(
          err.response?.data?.detail || "Failed to authenticate with Google"
        );
        setError(err.response?.data?.detail || "Authentication failed");
        setStatus("error");
      }
    };

    handleCallback();
  }, [searchParams, router, setUser, setToken, setError]);

  if (status === "loading") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600">
        <div className="bg-white rounded-2xl shadow-2xl p-12 text-center max-w-md">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-blue-600 rounded-full mb-6 animate-pulse">
            <span className="text-4xl">🔐</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Authenticating with Google
          </h1>
          <p className="text-gray-600 mb-6">
            Please wait while we complete your sign-in...
          </p>
          <div className="flex justify-center">
            <svg className="animate-spin h-10 w-10 text-purple-600" viewBox="0 0 24 24">
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-blue-500 to-indigo-600 px-4">
      <div className="bg-white rounded-2xl shadow-2xl p-12 text-center max-w-md">
        <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-6">
          <span className="text-4xl">❌</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Authentication Failed
        </h1>
        <p className="text-gray-600 mb-6">{errorMessage}</p>
        <button
          onClick={() => router.push("/login")}
          className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition"
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}
