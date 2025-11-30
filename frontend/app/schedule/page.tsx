"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { getDayAvailability, deleteEvent } from "@/lib/api";
import { format, startOfDay, isSameDay } from "date-fns";

export default function TodaySchedule() {
  const router = useRouter();
  const [selectedDate, setSelectedDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [daySlots, setDaySlots] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [selectedEvent, setSelectedEvent] = useState<any>(null);
  const [deletingEventId, setDeletingEventId] = useState<string | null>(null);
  const [userTimezone] = useState(() => {
    let tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const aliases: { [key: string]: string } = {
      'Asia/Calcutta': 'Asia/Kolkata',
    };
    return aliases[tz] || tz;
  });

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
      return;
    }
    loadSchedule();
  }, [router, selectedDate]);

  const loadSchedule = async () => {
    setIsLoading(true);
    setError("");
    try {
      const dateISO = new Date(selectedDate).toISOString();
      const availabilityData = await getDayAvailability(dateISO, userTimezone);
      setDaySlots(availabilityData.slots);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load schedule");
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm("Are you sure you want to delete this event?")) {
      return;
    }

    setDeletingEventId(eventId);
    setError("");
    setSuccess("");

    try {
      await deleteEvent(eventId);
      setSuccess("Event deleted successfully!");
      setSelectedEvent(null);
      loadSchedule();
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete event");
      setTimeout(() => setError(""), 5000);
    } finally {
      setDeletingEventId(null);
    }
  };

  const busySlots = daySlots.filter(slot => slot.events && slot.events.length > 0);
  const isToday = isSameDay(new Date(selectedDate), new Date());

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg">
                SM
              </div>
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                SmartMeet
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push("/app")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                📅 Schedule
              </button>
              <button
                onClick={() => router.push("/meetings")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                📋 History
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Date Selector */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-gray-800">
              {isToday ? "📅 Today's Schedule" : "📅 Schedule"}
            </h2>
            <div className="flex items-center space-x-4">
              <label className="text-gray-700 font-medium">Select Date:</label>
              <input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={() => setSelectedDate(format(new Date(), "yyyy-MM-dd"))}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Today
              </button>
            </div>
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            ⚠️ {error}
          </div>
        )}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
            ✅ {success}
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Loading schedule...</p>
          </div>
        )}

        {/* Schedule Display */}
        {!isLoading && (
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-xl p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">
              {format(new Date(selectedDate), "EEEE, MMMM d, yyyy")}
            </h3>

            {busySlots.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📭</div>
                <p className="text-gray-600 text-lg">No meetings scheduled for this day</p>
              </div>
            ) : (
              <div className="space-y-4">
                {busySlots.map((slot, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div className="w-2 h-12 bg-blue-600 rounded-full"></div>
                        <div>
                          <p className="text-lg font-bold text-gray-800">
                            {format(new Date(slot.start), "h:mm a")} - {format(new Date(slot.end), "h:mm a")}
                          </p>
                          <p className="text-sm text-gray-500">{slot.busy_minutes} minutes busy</p>
                        </div>
                      </div>
                    </div>

                    {/* Events in this slot */}
                    <div className="space-y-3 ml-5">
                      {slot.events.map((event: any, eventIndex: number) => (
                        <div
                          key={eventIndex}
                          className="bg-blue-50 border border-blue-200 rounded-lg p-4"
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-bold text-gray-800 mb-1">{event.title}</h4>
                              {event.description && (
                                <p className="text-sm text-gray-600 mb-2">{event.description}</p>
                              )}
                              <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span>⏰ {format(new Date(event.start), "h:mm a")} - {format(new Date(event.end), "h:mm a")}</span>
                                {event.attendees && event.attendees.length > 0 && (
                                  <span>👥 {event.attendees.length} attendee(s)</span>
                                )}
                              </div>
                              {event.location && (
                                <p className="text-sm text-gray-600 mt-1">📍 {event.location}</p>
                              )}
                            </div>
                            <div className="flex items-center space-x-2 ml-4">
                              {event.htmlLink && (
                                <a
                                  href={event.htmlLink}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="px-3 py-1 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                                >
                                  View
                                </a>
                              )}
                              <button
                                onClick={() => handleDeleteEvent(event.id)}
                                disabled={deletingEventId === event.id}
                                className="px-3 py-1 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm disabled:opacity-50"
                              >
                                {deletingEventId === event.id ? "..." : "Delete"}
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
