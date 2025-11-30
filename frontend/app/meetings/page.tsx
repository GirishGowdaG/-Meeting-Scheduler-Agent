"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getMeetingsHistory, deleteEvent } from "@/lib/api";
import { format, isPast } from "date-fns";

interface Meeting {
  id: string;
  title: string;
  description?: string;
  participants: Array<{ email?: string; name?: string }>;
  duration_minutes: number;
  start_time?: string;
  end_time?: string;
  timezone: string;
  event_id?: string;
  status: string;
  created_at: string;
}

export default function MeetingsHistory() {
  const router = useRouter();
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [activeTab, setActiveTab] = useState<"upcoming" | "completed">("upcoming");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }

    loadMeetings();
  }, [router]);

  const loadMeetings = async () => {
    try {
      const data = await getMeetingsHistory();
      setMeetings(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load meetings");
    } finally {
      setIsLoading(false);
    }
  };

  const upcomingMeetings = meetings.filter(m => 
    m.start_time && !isPast(new Date(m.start_time))
  );

  const completedMeetings = meetings.filter(m => 
    m.start_time && isPast(new Date(m.start_time))
  );

  const handleDeleteMeeting = async (meeting: Meeting) => {
    if (!meeting.event_id) {
      setError("Cannot delete meeting without event ID");
      return;
    }

    if (!confirm(`Are you sure you want to delete "${meeting.title}"? This will send cancellation emails to all attendees.`)) {
      return;
    }

    setDeletingId(meeting.id);
    setError("");
    setSuccess("");

    try {
      console.log("Deleting event:", meeting.event_id);
      await deleteEvent(meeting.event_id);
      
      console.log("Event deleted, updating state");
      // Remove from local state immediately
      setMeetings(prevMeetings => prevMeetings.filter(m => m.id !== meeting.id));
      
      setSuccess("Meeting deleted successfully!");
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      console.error("Delete error:", err);
      setError(err.response?.data?.detail || "Failed to delete meeting. Please try again.");
      setTimeout(() => setError(""), 5000);
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAll = async () => {
    const meetingsToDelete = activeTab === "upcoming" ? upcomingMeetings : completedMeetings;
    
    if (meetingsToDelete.length === 0) {
      return;
    }

    if (!confirm(`Are you sure you want to delete all ${activeTab} meetings (${meetingsToDelete.length} meetings)? This action cannot be undone.`)) {
      return;
    }

    setIsLoading(true);
    setError("");

    let deletedCount = 0;
    let failedCount = 0;

    for (const meeting of meetingsToDelete) {
      if (meeting.event_id) {
        try {
          await deleteEvent(meeting.event_id);
          deletedCount++;
        } catch (err) {
          failedCount++;
        }
      }
    }

    // Reload meetings
    await loadMeetings();
    
    if (failedCount === 0) {
      setSuccess(`Successfully deleted ${deletedCount} meeting(s)!`);
    } else {
      setError(`Deleted ${deletedCount} meeting(s), but ${failedCount} failed.`);
    }

    setTimeout(() => {
      setSuccess("");
      setError("");
    }, 5000);
  };

  const formatDateTime = (dateStr?: string) => {
    if (!dateStr) return "Not scheduled";
    const date = new Date(dateStr);
    return format(date, "MMM d, yyyy 'at' h:mm a");
  };

  const displayMeetings = activeTab === "upcoming" ? upcomingMeetings : completedMeetings;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Meeting History
              </h1>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push("/app")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                ➕ Schedule
              </button>
              <button
                onClick={() => router.push("/schedule")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                📅 Today's Schedule
              </button>
              <button
                onClick={() => {
                  localStorage.removeItem("token");
                  router.push("/");
                }}
                className="px-4 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Success/Error Messages */}
        {success && (
          <div className="mb-6 bg-green-50 border-2 border-green-200 text-green-700 px-6 py-4 rounded-xl flex items-start space-x-3 shadow-sm">
            <span className="text-2xl">✅</span>
            <p className="font-semibold">{success}</p>
          </div>
        )}
        
        {error && (
          <div className="mb-6 bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl flex items-start space-x-3 shadow-sm">
            <span className="text-2xl">⚠️</span>
            <p className="font-semibold">{error}</p>
          </div>
        )}

        {isLoading ? (
          <div className="text-center py-20">
            <div className="inline-block">
              <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600 mx-auto mb-6"></div>
              <p className="text-gray-600 font-medium">Loading your meetings...</p>
            </div>
          </div>
        ) : (
          <>
            {/* Tabs */}
            <div className="mb-6 flex items-center justify-between">
              <div className="flex space-x-2 bg-white rounded-xl p-2 shadow-md">
                <button
                  onClick={() => setActiveTab("upcoming")}
                  className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                    activeTab === "upcoming"
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  📅 Upcoming ({upcomingMeetings.length})
                </button>
                <button
                  onClick={() => setActiveTab("completed")}
                  className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                    activeTab === "completed"
                      ? "bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md"
                      : "text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  ✅ Completed ({completedMeetings.length})
                </button>
              </div>

              {displayMeetings.length > 0 && (
                <button
                  onClick={handleClearAll}
                  disabled={isLoading}
                  className="px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md hover:shadow-lg transition-all"
                >
                  🗑️ Clear All {activeTab === "upcoming" ? "Upcoming" : "Completed"}
                </button>
              )}
            </div>

            {displayMeetings.length === 0 ? (
              <div className="text-center py-20">
                <div className="bg-white rounded-3xl shadow-xl p-12 max-w-md mx-auto">
                  <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                    <span className="text-4xl">
                      {activeTab === "upcoming" ? "📅" : "✅"}
                    </span>
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-3">
                    No {activeTab === "upcoming" ? "Upcoming" : "Completed"} Meetings
                  </h3>
                  <p className="text-gray-600 mb-6">
                    {activeTab === "upcoming" 
                      ? "Start scheduling meetings with AI assistance"
                      : "Your completed meetings will appear here"}
                  </p>
                  {activeTab === "upcoming" && (
                    <button
                      onClick={() => router.push("/app")}
                      className="px-8 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 font-semibold shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
                    >
                      ➕ Schedule Your First Meeting
                    </button>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {displayMeetings.map((meeting) => (
                  <div
                    key={meeting.id}
                    className="bg-white rounded-2xl shadow-lg p-8 hover:shadow-xl transition-all border border-gray-100"
                  >
                    <div className="flex justify-between items-start mb-6">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center">
                            <span className="text-white text-lg">📅</span>
                          </div>
                          <h3 className="text-xl font-bold text-gray-900">
                            {meeting.title}
                          </h3>
                        </div>
                        {meeting.description && (
                          <p className="text-gray-600 ml-13 mb-3">
                            {meeting.description}
                          </p>
                        )}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6 mb-6">
                      <div className="space-y-3">
                        <div className="flex items-start space-x-3">
                          <span className="text-gray-400 text-lg">🕐</span>
                          <div>
                            <p className="text-xs text-gray-500 mb-1">When</p>
                            <p className="font-semibold text-gray-900">
                              {formatDateTime(meeting.start_time)}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-start space-x-3">
                          <span className="text-gray-400 text-lg">⏱️</span>
                          <div>
                            <p className="text-xs text-gray-500 mb-1">Duration</p>
                            <p className="font-semibold text-gray-900">
                              {meeting.duration_minutes} minutes
                            </p>
                          </div>
                        </div>
                      </div>
                      <div className="space-y-3">
                        {meeting.participants.length > 0 && (
                          <div className="flex items-start space-x-3">
                            <span className="text-gray-400 text-lg">👥</span>
                            <div className="flex-1">
                              <p className="text-xs text-gray-500 mb-2">Participants</p>
                              <div className="flex flex-wrap gap-2">
                                {meeting.participants.map((p, idx) => (
                                  <span key={idx} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-lg text-xs font-medium">
                                    {p.email || p.name || "Unknown"}
                                  </span>
                                ))}
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center justify-between pt-6 border-t border-gray-200">
                      {meeting.event_id && (
                        <a
                          href="https://calendar.google.com"
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 font-semibold shadow-md hover:shadow-lg transition-all"
                        >
                          <span className="mr-2">📅</span>
                          View in Calendar
                        </a>
                      )}
                      
                      <button
                        onClick={() => handleDeleteMeeting(meeting)}
                        disabled={deletingId === meeting.id}
                        className="px-6 py-3 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-md hover:shadow-lg transition-all"
                      >
                        {deletingId === meeting.id ? (
                          <span className="flex items-center">
                            <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Deleting...
                          </span>
                        ) : (
                          "🗑️ Delete"
                        )}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
