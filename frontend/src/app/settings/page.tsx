"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";

export default function SettingsPage() {
  const router = useRouter();
  const { isAuthenticated, user } = useAuthStore();
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  // Notification preferences
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [telegramEnabled, setTelegramEnabled] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState("");
  const [reminderTime, setReminderTime] = useState("15"); // minutes before
  const [autoContextGeneration, setAutoContextGeneration] = useState(true);

  // Google Calendar settings
  const [googleCalendarConnected, setGoogleCalendarConnected] = useState(false);
  const [autoSync, setAutoSync] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
    }
  }, [isAuthenticated, router]);

  const handleSave = async () => {
    setSaving(true);
    setError("");
    setSuccess(false);

    try {
      // In a real app, you would save these settings to the backend
      // For now, we'll just simulate the save
      await new Promise((resolve) => setTimeout(resolve, 1000));

      // Save to localStorage for demonstration
      const settings = {
        emailEnabled,
        telegramEnabled,
        telegramChatId,
        reminderTime,
        autoContextGeneration,
        googleCalendarConnected,
        autoSync,
      };
      localStorage.setItem("userSettings", JSON.stringify(settings));

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleConnectGoogleCalendar = () => {
    // In a real app, this would redirect to Google OAuth
    alert("Google Calendar OAuth integration would redirect here");
  };

  const handleDisconnectGoogleCalendar = () => {
    setGoogleCalendarConnected(false);
    setAutoSync(false);
  };

  const handleConnectTelegram = () => {
    alert(
      "To connect Telegram:\n\n1. Start a chat with @ContextMeet_Bot on Telegram\n2. Send /start command\n3. Copy your Chat ID\n4. Paste it in the field below"
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/dashboard")}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Back
            </button>
            <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-green-800 text-sm">✓ Settings saved successfully!</p>
          </div>
        )}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        <div className="space-y-6">
          {/* Account Section */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Account</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email
                </label>
                <input
                  type="email"
                  value={user?.email || ""}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name
                </label>
                <input
                  type="text"
                  value={user?.name || ""}
                  disabled
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600 cursor-not-allowed"
                />
              </div>
            </div>
          </div>

          {/* Notification Preferences */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Notification Preferences
            </h2>
            <div className="space-y-6">
              {/* Email Notifications */}
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="email_notifications"
                    type="checkbox"
                    checked={emailEnabled}
                    onChange={(e) => setEmailEnabled(e.target.checked)}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                </div>
                <div className="ml-3">
                  <label
                    htmlFor="email_notifications"
                    className="text-sm font-medium text-gray-700"
                  >
                    Email Notifications
                  </label>
                  <p className="text-xs text-gray-500">
                    Receive meeting reminders via email
                  </p>
                </div>
              </div>

              {/* Telegram Notifications */}
              <div>
                <div className="flex items-start mb-2">
                  <div className="flex items-center h-5">
                    <input
                      id="telegram_notifications"
                      type="checkbox"
                      checked={telegramEnabled}
                      onChange={(e) => setTelegramEnabled(e.target.checked)}
                      className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                    />
                  </div>
                  <div className="ml-3">
                    <label
                      htmlFor="telegram_notifications"
                      className="text-sm font-medium text-gray-700"
                    >
                      Telegram Notifications
                    </label>
                    <p className="text-xs text-gray-500">
                      Receive meeting reminders on Telegram
                    </p>
                  </div>
                </div>
                {telegramEnabled && (
                  <div className="ml-7 mt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Telegram Chat ID
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={telegramChatId}
                        onChange={(e) => setTelegramChatId(e.target.value)}
                        placeholder="Enter your Telegram Chat ID"
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      />
                      <button
                        onClick={handleConnectTelegram}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        How to Connect
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Reminder Time */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Reminder Time
                </label>
                <select
                  value={reminderTime}
                  onChange={(e) => setReminderTime(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="5">5 minutes before</option>
                  <option value="10">10 minutes before</option>
                  <option value="15">15 minutes before</option>
                  <option value="30">30 minutes before</option>
                  <option value="60">1 hour before</option>
                  <option value="120">2 hours before</option>
                  <option value="1440">1 day before</option>
                </select>
              </div>
            </div>
          </div>

          {/* AI Context Settings */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              AI Context Generation
            </h2>
            <div className="space-y-4">
              <div className="flex items-start">
                <div className="flex items-center h-5">
                  <input
                    id="auto_context"
                    type="checkbox"
                    checked={autoContextGeneration}
                    onChange={(e) => setAutoContextGeneration(e.target.checked)}
                    className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                  />
                </div>
                <div className="ml-3">
                  <label
                    htmlFor="auto_context"
                    className="text-sm font-medium text-gray-700"
                  >
                    Auto-generate AI Context
                  </label>
                  <p className="text-xs text-gray-500">
                    Automatically generate AI context for new meetings
                  </p>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-900 mb-2">
                  💡 About AI Context
                </h4>
                <p className="text-xs text-blue-800">
                  Our AI analyzes your meeting details to generate:
                </p>
                <ul className="text-xs text-blue-800 ml-4 mt-1 space-y-1">
                  <li>• Meeting type classification</li>
                  <li>• Key topics and discussion points</li>
                  <li>• Personalized preparation checklist</li>
                  <li>• Attendee insights and context</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Google Calendar Integration */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Google Calendar Integration
            </h2>
            <div className="space-y-4">
              {googleCalendarConnected ? (
                <>
                  <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                        <span className="text-xl">✓</span>
                      </div>
                      <div>
                        <p className="text-sm font-medium text-green-900">
                          Google Calendar Connected
                        </p>
                        <p className="text-xs text-green-700">
                          Your calendar is synced
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={handleDisconnectGoogleCalendar}
                      className="px-4 py-2 text-sm border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>

                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="auto_sync"
                        type="checkbox"
                        checked={autoSync}
                        onChange={(e) => setAutoSync(e.target.checked)}
                        className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                      />
                    </div>
                    <div className="ml-3">
                      <label
                        htmlFor="auto_sync"
                        className="text-sm font-medium text-gray-700"
                      >
                        Auto-sync Calendar
                      </label>
                      <p className="text-xs text-gray-500">
                        Automatically sync meetings from Google Calendar
                      </p>
                    </div>
                  </div>
                </>
              ) : (
                <button
                  onClick={handleConnectGoogleCalendar}
                  className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-400 hover:bg-purple-50 transition-colors flex items-center justify-center gap-3"
                >
                  <svg className="w-6 h-6" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    />
                  </svg>
                  <span className="text-gray-700 font-medium">
                    Connect Google Calendar
                  </span>
                </button>
              )}
            </div>
          </div>

          {/* Save Button */}
          <div className="flex justify-end">
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-8 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              {saving ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                  Saving...
                </>
              ) : (
                "Save Settings"
              )}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
