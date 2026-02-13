"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, restoreSession } = useAuthStore();

  useEffect(() => {
    const checkAuth = async () => {
      await restoreSession();
      if (isAuthenticated) {
        router.push("/dashboard");
      } else {
        router.push("/login");
      }
    };
    checkAuth();
  }, [isAuthenticated, router, restoreSession]);

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-blue-600 to-indigo-600">
      <div className="text-center text-white">
        <div className="mb-6">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-white"></div>
        </div>
        <h1 className="text-4xl font-bold mb-4">ContextMeet</h1>
        <p className="text-xl opacity-90">
          AI-Powered Meeting Context Assistant
        </p>
        <p className="text-sm opacity-75 mt-4">
          Loading your workspace...
        </p>
      </div>
    </main>
  );
}
