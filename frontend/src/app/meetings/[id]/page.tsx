"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useMeetingStore } from "@/store/meetings";
import { useContextStore } from "@/store/contexts";
import { format } from "date-fns";

export default function MeetingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const meetingId = params.id as string;

  const {
    currentMeeting,
    fetchMeeting,
    deleteMeeting,
    isLoading: meetingLoading,
  } = useMeetingStore();
  const {
    currentContext,
    fetchContext,
    generateContext,
    isLoading: contextLoading,
    isGenerating,
  } = useContextStore();

  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    if (meetingId) {
      fetchMeeting(meetingId);
      fetchContext(meetingId);
    }
  }, [meetingId]);

  const handleGenerateContext = async () => {
    await generateContext(meetingId, true);
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await deleteMeeting(meetingId);
      router.push("/dashboard");
    } catch (error) {
      setIsDeleting(false);
      setShowDeleteConfirm(false);
    }
  };

  if (meetingLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <svg
          className="animate-spin h-12 w-12 text-purple-600"
          viewBox="0 0 24 24"
        >
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
    );
  }

  if (!currentMeeting) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-gray-600">Meeting not found</p>
          <button
            onClick={() => router.push("/dashboard")}
            className="mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <div className="flex items-center space-x-3 mb-4">
              <div className="flex-shrink-0 w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900">
                  Delete Meeting
                </h3>
                <p className="text-sm text-gray-500">
                  This action cannot be undone
                </p>
              </div>
            </div>

            <p className="text-gray-700 mb-6">
              Are you sure you want to delete "
              <span className="font-semibold">{currentMeeting?.title}</span>"?
              All associated data including AI context and notifications will be
              permanently removed.
            </p>

            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isDeleting}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isDeleting}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isDeleting ? (
                  <span className="flex items-center space-x-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
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
                    <span>Deleting...</span>
                  </span>
                ) : (
                  "Delete Meeting"
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={() => router.push("/dashboard")}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 19l-7-7 7-7"
                />
              </svg>
              Back
            </button>

            <div className="flex items-center space-x-3">
              {/* Edit Button */}
              <button
                onClick={() => router.push(`/meetings/${meetingId}/edit`)}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition flex items-center space-x-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
                <span>Edit</span>
              </button>

              {/* Delete Button */}
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="px-4 py-2 bg-red-100 text-red-700 rounded-lg font-medium hover:bg-red-200 transition flex items-center space-x-2"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                  />
                </svg>
                <span>Delete</span>
              </button>

              {/* Join Meeting Button */}
              {currentMeeting.meeting_link && (
                <a
                  href={currentMeeting.meeting_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition flex items-center space-x-2"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                    />
                  </svg>
                  <span>Join Meeting</span>
                </a>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Meeting Details */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                {currentMeeting.title}
              </h2>

              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <svg
                    className="w-5 h-5 text-gray-500 mt-0.5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <div>
                    <p className="text-sm font-medium text-gray-700">
                      Date & Time
                    </p>
                    <p className="text-sm text-gray-900">
                      {format(
                        new Date(currentMeeting.start_time),
                        "MMMM dd, yyyy",
                      )}
                    </p>
                    <p className="text-sm text-gray-600">
                      {format(new Date(currentMeeting.start_time), "h:mm a")} -{" "}
                      {format(new Date(currentMeeting.end_time), "h:mm a")}
                    </p>
                  </div>
                </div>

                {currentMeeting.description && (
                  <div className="flex items-start space-x-3">
                    <svg
                      className="w-5 h-5 text-gray-500 mt-0.5"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                      />
                    </svg>
                    <div>
                      <p className="text-sm font-medium text-gray-700">
                        Description
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        {currentMeeting.description}
                      </p>
                    </div>
                  </div>
                )}

                {currentMeeting.attendees &&
                  currentMeeting.attendees.length > 0 && (
                    <div className="flex items-start space-x-3">
                      <svg
                        className="w-5 h-5 text-gray-500 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                        />
                      </svg>
                      <div>
                        <p className="text-sm font-medium text-gray-700">
                          Attendees ({currentMeeting.attendees.length})
                        </p>
                        <ul className="mt-1 space-y-1">
                          {currentMeeting.attendees.map((attendee, idx) => (
                            <li key={idx} className="text-sm text-gray-600">
                              {attendee.name || attendee.email}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
              </div>
            </div>
          </div>

          {/* AI Context */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900 flex items-center space-x-2">
                  <span>🤖</span>
                  <span>AI Context</span>
                </h2>

                {!currentContext && !isGenerating && (
                  <button
                    onClick={handleGenerateContext}
                    className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition"
                  >
                    Generate Context
                  </button>
                )}

                {currentContext && (
                  <button
                    onClick={handleGenerateContext}
                    disabled={isGenerating}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition disabled:opacity-50"
                  >
                    {isGenerating ? "Regenerating..." : "Regenerate"}
                  </button>
                )}
              </div>

              {isGenerating && (
                <div className="flex flex-col items-center justify-center py-16">
                  <svg
                    className="animate-spin h-12 w-12 text-purple-600 mb-4"
                    viewBox="0 0 24 24"
                  >
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
                  <p className="text-lg font-medium text-gray-900">
                    Generating AI Context...
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    Mistral AI is analyzing your meeting
                  </p>
                </div>
              )}

              {!isGenerating && !currentContext && (
                <div className="text-center py-16">
                  <div className="text-6xl mb-4">🧠</div>
                  <p className="text-lg text-gray-600 mb-2">
                    No AI context generated yet
                  </p>
                  <p className="text-sm text-gray-500">
                    Click "Generate Context" to get AI-powered insights
                  </p>
                </div>
              )}

              {currentContext && !isGenerating && (
                <div className="space-y-6">
                  {/* Meeting Type & Brief */}
                  <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-5 border-l-4 border-purple-500">
                    <div className="flex items-center justify-between mb-3">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        {currentContext.meeting_type
                          .replace("_", " ")
                          .toUpperCase()}
                      </span>
                      <span className="text-xs text-gray-500">
                        Confidence: {currentContext.confidence_score}%
                      </span>
                    </div>
                    <p className="text-gray-800 leading-relaxed">
                      {currentContext.ai_brief}
                    </p>
                  </div>

                  {/* Key Topics */}
                  {currentContext.key_topics &&
                    currentContext.key_topics.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                          <span>📌</span>
                          <span>Key Topics</span>
                        </h3>
                        <ul className="space-y-2">
                          {currentContext.key_topics.map((topic, idx) => (
                            <li
                              key={idx}
                              className="flex items-start space-x-2"
                            >
                              <span className="text-purple-600 mt-1">•</span>
                              <span className="text-gray-700">{topic}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                  {/* Preparation Checklist */}
                  {currentContext.preparation_checklist &&
                    currentContext.preparation_checklist.length > 0 && (
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                          <span>✅</span>
                          <span>Preparation Checklist</span>
                        </h3>
                        <ul className="space-y-2">
                          {currentContext.preparation_checklist.map(
                            (item, idx) => (
                              <li
                                key={idx}
                                className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg"
                              >
                                <input
                                  type="checkbox"
                                  className="mt-1 rounded text-purple-600 focus:ring-purple-500"
                                />
                                <span className="text-gray-700">
                                  {typeof item === "string" ? item : item.text}
                                </span>
                              </li>
                            ),
                          )}
                        </ul>
                      </div>
                    )}

                  {/* Attendee Context */}
                  {currentContext.attendee_context &&
                    Object.keys(currentContext.attendee_context).length > 0 && (
                      <div>
                        <h3 className="font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                          <span>👥</span>
                          <span>Attendee Insights</span>
                        </h3>
                        <div className="space-y-2">
                          {Object.entries(currentContext.attendee_context).map(
                            ([email, context]) => (
                              <div
                                key={email}
                                className="p-3 bg-blue-50 rounded-lg"
                              >
                                <p className="text-sm font-medium text-gray-900">
                                  {email}
                                </p>
                                <p className="text-sm text-gray-600 mt-1">
                                  {context}
                                </p>
                              </div>
                            ),
                          )}
                        </div>
                      </div>
                    )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
