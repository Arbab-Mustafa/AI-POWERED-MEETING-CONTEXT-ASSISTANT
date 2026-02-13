"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMeetingStore } from "@/store/meetings";
import { useContextStore } from "@/store/contexts";

export default function NewMeetingPage() {
  const router = useRouter();
  const { createMeeting, isLoading: creatingMeeting } = useMeetingStore();
  const { generateContext, isGenerating } = useContextStore();
  const [error, setError] = useState<string>("");
  const [autoGenerateContext, setAutoGenerateContext] = useState(true);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    start_time: "",
    end_time: "",
    attendees_input: "",
    meeting_link: "",
    location: "",
  });

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validation
    if (!formData.title.trim()) {
      setError("Meeting title is required");
      return;
    }
    if (!formData.start_time) {
      setError("Start time is required");
      return;
    }
    if (!formData.end_time) {
      setError("End time is required");
      return;
    }
    if (new Date(formData.start_time) >= new Date(formData.end_time)) {
      setError("End time must be after start time");
      return;
    }

    // Parse attendees (comma-separated emails)
    const attendees = formData.attendees_input
      .split(",")
      .map((email) => email.trim())
      .filter((email) => email.length > 0);

    try {
      const meetingData = {
        title: formData.title,
        description: formData.description || undefined,
        start_time: new Date(formData.start_time).toISOString(),
        end_time: new Date(formData.end_time).toISOString(),
        attendees: attendees.length > 0 ? attendees : undefined,
        meeting_link: formData.meeting_link || undefined,
        location: formData.location || undefined,
      };

      const newMeeting = await createMeeting(meetingData);

      // Auto-generate AI context if enabled
      if (autoGenerateContext && newMeeting?.id) {
        try {
          await generateContext(newMeeting.id);
        } catch (err) {
          console.error("Failed to generate context:", err);
          // Don't block navigation if context generation fails
        }
      }

      // Redirect to meeting detail page
      if (newMeeting?.id) {
        router.push(`/meetings/${newMeeting.id}`);
      } else {
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(err.message || "Failed to create meeting");
    }
  };

  const isLoading = creatingMeeting || isGenerating;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => router.push("/dashboard")}
              className="text-gray-600 hover:text-gray-900 transition-colors"
            >
              ← Back
            </button>
            <h1 className="text-2xl font-bold text-gray-900">
              Create New Meeting
            </h1>
          </div>
        </div>
      </header>

      {/* Form */}
      <main className="max-w-4xl mx-auto px-6 py-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Meeting Title */}
            <div>
              <label
                htmlFor="title"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Meeting Title *
              </label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="e.g., Weekly Team Sync"
                required
              />
            </div>

            {/* Description */}
            <div>
              <label
                htmlFor="description"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Description
              </label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
                placeholder="Provide details about the meeting agenda, topics to discuss, etc."
              />
            </div>

            {/* Date & Time */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label
                  htmlFor="start_time"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Start Time *
                </label>
                <input
                  type="datetime-local"
                  id="start_time"
                  name="start_time"
                  value={formData.start_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label
                  htmlFor="end_time"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  End Time *
                </label>
                <input
                  type="datetime-local"
                  id="end_time"
                  name="end_time"
                  value={formData.end_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            {/* Attendees */}
            <div>
              <label
                htmlFor="attendees_input"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Attendees
              </label>
              <input
                type="text"
                id="attendees_input"
                name="attendees_input"
                value={formData.attendees_input}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="Enter email addresses separated by commas"
              />
              <p className="mt-1 text-sm text-gray-500">
                Separate multiple email addresses with commas (e.g.,
                john@example.com, jane@example.com)
              </p>
            </div>

            {/* Meeting Link */}
            <div>
              <label
                htmlFor="meeting_link"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Meeting Link
              </label>
              <input
                type="url"
                id="meeting_link"
                name="meeting_link"
                value={formData.meeting_link}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="https://meet.google.com/xxx-xxxx-xxx"
              />
            </div>

            {/* Location */}
            <div>
              <label
                htmlFor="location"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Location
              </label>
              <input
                type="text"
                id="location"
                name="location"
                value={formData.location}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                placeholder="e.g., Conference Room A or Virtual"
              />
            </div>

            {/* Auto-generate Context */}
            <div className="flex items-start">
              <div className="flex items-center h-5">
                <input
                  id="auto_generate"
                  type="checkbox"
                  checked={autoGenerateContext}
                  onChange={(e) => setAutoGenerateContext(e.target.checked)}
                  className="w-4 h-4 text-purple-600 border-gray-300 rounded focus:ring-purple-500"
                />
              </div>
              <div className="ml-3">
                <label
                  htmlFor="auto_generate"
                  className="text-sm font-medium text-gray-700"
                >
                  Auto-generate AI Context
                </label>
                <p className="text-xs text-gray-500">
                  Automatically generate meeting preparation context using AI
                  after creating the meeting
                </p>
              </div>
            </div>

            {/* Buttons */}
            <div className="flex gap-4 pt-4">
              <button
                type="button"
                onClick={() => router.push("/dashboard")}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white"></div>
                    {isGenerating
                      ? "Generating Context..."
                      : "Creating Meeting..."}
                  </>
                ) : (
                  "Create Meeting"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Tips Section */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            💡 Tips for Better AI Context
          </h3>
          <ul className="space-y-2 text-sm text-blue-800">
            <li>
              • Provide a descriptive title that clearly indicates the meeting
              purpose
            </li>
            <li>
              • Include key topics, goals, or agenda items in the description
            </li>
            <li>• Add attendee emails to get personalized insights</li>
            <li>
              • The AI will analyze all meeting details to generate relevant
              preparation context
            </li>
          </ul>
        </div>
      </main>
    </div>
  );
}
