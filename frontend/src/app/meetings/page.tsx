"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useMeetingStore } from "@/store/meetings";
import { useAuthStore } from "@/store/auth";
import { format, parseISO, isPast, isFuture, isToday } from "date-fns";

type FilterStatus = "all" | "upcoming" | "today" | "past";

export default function AllMeetingsPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const { meetings, isLoading, error, fetchMeetings } = useMeetingStore();
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<FilterStatus>("all");

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    fetchMeetings();
  }, [isAuthenticated, router, fetchMeetings]);

  // Filter meetings based on search and status
  const filteredMeetings = meetings.filter((meeting) => {
    // Search filter
    const matchesSearch =
      searchQuery === "" ||
      meeting.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      meeting.description?.toLowerCase().includes(searchQuery.toLowerCase());

    if (!matchesSearch) return false;

    // Status filter
    const meetingDate = parseISO(meeting.start_time);
    switch (filterStatus) {
      case "today":
        return isToday(meetingDate);
      case "upcoming":
        return isFuture(meetingDate) && !isToday(meetingDate);
      case "past":
        return isPast(meetingDate) && !isToday(meetingDate);
      default:
        return true;
    }
  });

  const getMeetingStatus = (startTime: string) => {
    const meetingDate = parseISO(startTime);
    if (isToday(meetingDate))
      return { label: "Today", color: "bg-green-100 text-green-800" };
    if (isFuture(meetingDate))
      return { label: "Upcoming", color: "bg-blue-100 text-blue-800" };
    return { label: "Past", color: "bg-gray-100 text-gray-600" };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push("/dashboard")}
                className="text-gray-600 hover:text-gray-900 transition-colors"
              >
                ← Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  All Meetings
                </h1>
                <p className="text-sm text-gray-600 mt-1">
                  {filteredMeetings.length} meeting
                  {filteredMeetings.length !== 1 ? "s" : ""} found
                </p>
              </div>
            </div>
            <button
              onClick={() => router.push("/meetings/new")}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-colors"
            >
              + New Meeting
            </button>
          </div>
        </div>
      </header>

      {/* Filters & Search */}
      <div className="max-w-7xl mx-auto px-6 py-6">
        <div className="bg-white rounded-lg shadow-sm p-4 mb-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <input
                type="text"
                placeholder="Search meetings by title or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              />
            </div>

            {/* Status Filter */}
            <div className="flex gap-2">
              <button
                onClick={() => setFilterStatus("all")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === "all"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                All
              </button>
              <button
                onClick={() => setFilterStatus("today")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === "today"
                    ? "bg-green-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                Today
              </button>
              <button
                onClick={() => setFilterStatus("upcoming")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === "upcoming"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                Upcoming
              </button>
              <button
                onClick={() => setFilterStatus("past")}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  filterStatus === "past"
                    ? "bg-gray-600 text-white"
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                Past
              </button>
            </div>
          </div>
        </div>

        {/* Meetings List */}
        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <div className="text-center">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-purple-600 mb-4"></div>
              <p className="text-gray-600">Loading meetings...</p>
            </div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
            <p className="text-red-800">{error}</p>
            <button
              onClick={() => fetchMeetings()}
              className="mt-4 px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Retry
            </button>
          </div>
        ) : filteredMeetings.length === 0 ? (
          <div className="bg-white rounded-lg shadow-sm p-12 text-center">
            <div className="text-6xl mb-4">📅</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No meetings found
            </h3>
            <p className="text-gray-600 mb-6">
              {searchQuery || filterStatus !== "all"
                ? "Try adjusting your search or filters"
                : "Create your first meeting to get started"}
            </p>
            {searchQuery === "" && filterStatus === "all" && (
              <button
                onClick={() => router.push("/meetings/new")}
                className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700"
              >
                Create Meeting
              </button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredMeetings.map((meeting) => {
              const status = getMeetingStatus(meeting.start_time);
              const startDate = parseISO(meeting.start_time);
              const endDate = parseISO(meeting.end_time);

              return (
                <div
                  key={meeting.id}
                  onClick={() => router.push(`/meetings/${meeting.id}`)}
                  className="bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow cursor-pointer border border-gray-200 hover:border-purple-300"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {meeting.title}
                        </h3>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${status.color}`}
                        >
                          {status.label}
                        </span>
                        {meeting.has_context && (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                            ✨ AI Ready
                          </span>
                        )}
                      </div>

                      {meeting.description && (
                        <p className="text-gray-600 mb-3 line-clamp-2">
                          {meeting.description}
                        </p>
                      )}

                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <span>📅</span>
                          <span>{format(startDate, "MMM dd, yyyy")}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <span>🕐</span>
                          <span>
                            {format(startDate, "h:mm a")} -{" "}
                            {format(endDate, "h:mm a")}
                          </span>
                        </div>
                        {meeting.attendees && meeting.attendees.length > 0 && (
                          <div className="flex items-center gap-1">
                            <span>👥</span>
                            <span>{meeting.attendees.length} attendees</span>
                          </div>
                        )}
                        {meeting.location && (
                          <div className="flex items-center gap-1">
                            <span>📍</span>
                            <span className="truncate max-w-xs">
                              {meeting.location}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex gap-2 ml-4">
                      {meeting.meeting_link && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            window.open(meeting.meeting_link, "_blank");
                          }}
                          className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                        >
                          Join
                        </button>
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(`/meetings/${meeting.id}`);
                        }}
                        className="px-4 py-2 text-sm bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                      >
                        View Details
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
