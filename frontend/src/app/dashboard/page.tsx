"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/auth";
import { useMeetingStore } from "@/store/meetings";
import { useContextStore } from "@/store/contexts";
import { format, isToday, isTomorrow, isPast } from "date-fns";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();
  const { meetings, isLoading, fetchMeetings, syncGoogleCalendar } = useMeetingStore();
  const { contexts, fetchContext } = useContextStore();
  const [isSyncing, setIsSyncing] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
 router.push("/login");
      return;
    }
    fetchMeetings();
  }, [isAuthenticated]);

  const handleSync = async () => {
    setIsSyncing(true);
    await syncGoogleCalendar();
    setIsSyncing(false);
  };

  const getMeetingTimeLabel = (startTime: string) => {
    const date = new Date(startTime);
    if (isToday(date)) return "Today";
    if (isTomorrow(date)) return "Tomorrow";
    if (isPast(date)) return "Past";
    return format(date, "MMM dd");
  };

  const upcomingMeetings = meetings
    .filter(m => !isPast(new Date(m.start_time)))
    .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
    .slice(0, 5);

  const todayMeetings = meetings.filter(m => isToday(new Date(m.start_time)));

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">ContextMeet</h1>
                <p className="text-sm text-gray-500">Welcome back, {user?.name}!</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleSync}
                disabled={isSyncing}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition disabled:opacity-50 flex items-center space-x-2"
              >
                <svg className={`w-5 h-5 ${isSyncing ? 'animate-spin' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>{isSyncing ? "Syncing..." : "Sync Calendar"}</span>
              </button>
              
              <button
                onClick={() => router.push("/meetings/new")}
                className="px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                <span>New Meeting</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Today's Meetings */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Today's Meetings</h2>
              
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <svg className="animate-spin h-8 w-8 text-purple-600" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </div>
              ) : todayMeetings.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📅</div>
                  <p className="text-gray-500 text-lg">No meetings scheduled for today</p>
                  <p className="text-gray-400 text-sm mt-2">Enjoy your free time!</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {todayMeetings.map((meeting) => (
                    <MeetingCard 
                      key={meeting.id} 
                      meeting={meeting} 
                      onClick={() => router.push(`/meetings/${meeting.id}`)}
                    />
                  ))}
                </div>
              )}
            </div>

            {/* Upcoming Meetings */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Upcoming Meetings</h2>
              
              {upcomingMeetings.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No upcoming meetings</p>
              ) : (
                <div className="space-y-3">
                  {upcomingMeetings.map((meeting) => (
                    <div
                      key={meeting.id}
                      onClick={() => router.push(`/meetings/${meeting.id}`)}
                      className="p-4 border border-gray-200 rounded-lg hover:border-purple-300 hover:bg-purple-50 transition cursor-pointer"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">{meeting.title}</h3>
                          <p className="text-sm text-gray-600 mt-1">
                            {format(new Date(meeting.start_time), "MMM dd, h:mm a")}
                          </p>
                          {meeting.attendees && meeting.attendees.length > 0 && (
                            <p className="text-xs text-gray-500 mt-1">
                              {meeting.attendees.length} attendee{meeting.attendees.length > 1 ? 's' : ''}
                            </p>
                          )}
                        </div>
                        {meeting.context_generated && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            AI Ready
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Stats Sidebar */}
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-purple-600 to-blue-600 rounded-xl shadow-sm p-6 text-white">
              <h3 className="text-lg font-semibold mb-4">Quick Stats</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-purple-100 text-sm">Total Meetings</p>
                  <p className="text-3xl font-bold">{meetings.length}</p>
                </div>
                <div>
                  <p className="text-purple-100 text-sm">Today</p>
                  <p className="text-3xl font-bold">{todayMeetings.length}</p>
                </div>
                <div>
                  <p className="text-purple-100 text-sm">AI Contexts</p>
                  <p className="text-3xl font-bold">
                    {meetings.filter(m => m.context_generated).length}
                  </p>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="font-semibold text-gray-900 mb-4">Quick Actions</h3>
              <div className="space-y-2">
                <button 
                  onClick={() => router.push("/meetings")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition flex items-center space-x-3"
                >
                  <span className="text-2xl">📋</span>
                  <span className="text-gray-700">View All Meetings</span>
                </button>
                <button 
                  onClick={() => router.push("/settings")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition flex items-center space-x-3"
                >
                  <span className="text-2xl">⚙️</span>
                  <span className="text-gray-700">Settings</span>
                </button>
                <button 
                  onClick={() => router.push("/profile")}
                  className="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition flex items-center space-x-3"
                >
                  <span className="text-2xl">👤</span>
                  <span className="text-gray-700">Profile</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function MeetingCard({ meeting, onClick }: any) {
  return (
    <div
      onClick={onClick}
      className="p-5 border-l-4 border-purple-500 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg hover:shadow-md transition cursor-pointer"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-bold text-gray-900 text-lg">{meeting.title}</h3>
          <p className="text-sm text-gray-600 mt-1">
            {format(new Date(meeting.start_time), "h:mm a")} - {format(new Date(meeting.end_time), "h:mm a")}
          </p>
          {meeting.description && (
            <p className="text-sm text-gray-700 mt-2 line-clamp-2">{meeting.description}</p>
          )}
          {meeting.attendees && meeting.attendees.length > 0 && (
            <div className="flex items-center mt-3 space-x-2">
              <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span className="text-sm text-gray-600">{meeting.attendees.length} attendee{meeting.attendees.length > 1 ? 's' : ''}</span>
            </div>
          )}
        </div>
        <div className="ml-4 flex flex-col items-end space-y-2">
          {meeting.context_generated && (
            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              ✨ AI Ready
            </span>
          )}
          {meeting.meeting_link && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                window.open(meeting.meeting_link, '_blank');
              }}
              className="px-3 py-1 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
            >
              Join
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
