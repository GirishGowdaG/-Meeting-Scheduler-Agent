"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { createEvent, getDayAvailability, deleteEvent } from "@/lib/api";
import { format, addDays } from "date-fns";

export default function SchedulerApp() {
  const router = useRouter();
  const [meetingTitle, setMeetingTitle] = useState("");
  const [meetingDate, setMeetingDate] = useState("");
  const [meetingTime, setMeetingTime] = useState("");
  const [duration, setDuration] = useState("30");
  const [participants, setParticipants] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [daySlots, setDaySlots] = useState<any[]>([]);
  const [selectedBusySlot, setSelectedBusySlot] = useState<any>(null);
  const [deletingEventId, setDeletingEventId] = useState<string | null>(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [userTimezone] = useState(() => {
    let tz = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const aliases: { [key: string]: string } = {
      'Asia/Calcutta': 'Asia/Kolkata',
    };
    return aliases[tz] || tz;
  });

  const getTimezoneDisplay = () => {
    const date = new Date();
    const offset = -date.getTimezoneOffset();
    const hours = Math.floor(Math.abs(offset) / 60);
    const minutes = Math.abs(offset) % 60;
    const sign = offset >= 0 ? '+' : '-';
    return `UTC${sign}${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
  };

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/");
    }
    
    // Set default date to tomorrow
    const tomorrow = addDays(new Date(), 1);
    setMeetingDate(format(tomorrow, "yyyy-MM-dd"));
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validation
    if (!meetingTitle.trim()) {
      setError("Please enter a meeting title");
      return;
    }
    if (!meetingDate) {
      setError("Please select a date");
      return;
    }


    setIsLoading(true);
    setError("");
    setSuccess("");
    setDaySlots([]);

    try {
      // Fetch day availability (9 AM - 6 PM hourly slots)
      const dateISO = new Date(meetingDate).toISOString();
      const availabilityData = await getDayAvailability(dateISO, userTimezone);
      setDaySlots(availabilityData.slots);
    } catch (err: any) {
      console.error("Error details:", err.response?.data);
      const errorMsg = err.response?.data?.detail 
        ? (typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : JSON.stringify(err.response.data.detail))
        : "Failed to process request";
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm("Are you sure you want to delete this event? This will send cancellation emails to all attendees.")) {
      return;
    }

    setDeletingEventId(eventId);
    setError("");

    try {
      await deleteEvent(eventId);
      setSuccess("Event deleted successfully!");
      
      // Refresh the day slots
      if (meetingDate) {
        const dateISO = new Date(meetingDate).toISOString();
        const availabilityData = await getDayAvailability(dateISO, userTimezone);
        setDaySlots(availabilityData.slots);
      }
      
      // Close modal
      setSelectedBusySlot(null);
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(""), 3000);
    } catch (err: any) {
      console.error("Error deleting event:", err);
      setError("Failed to delete event. Please try again.");
    } finally {
      setDeletingEventId(null);
    }
  };

  const handleConfirm = async () => {
    if (!meetingDate || !meetingTime) return;

    setIsLoading(true);
    setError("");

    try {
      // Create datetime string without timezone conversion
      // Format: YYYY-MM-DDTHH:MM:SS (will be interpreted in user's timezone by backend)
      const startDateTimeStr = `${meetingDate}T${meetingTime}:00`;
      
      // Calculate end time
      const [year, month, day] = meetingDate.split('-').map(Number);
      const [hours, minutes] = meetingTime.split(':').map(Number);
      const startDateTime = new Date(year, month - 1, day, hours, minutes, 0);
      const endDateTime = new Date(startDateTime.getTime() + parseInt(duration) * 60000);
      
      const endYear = endDateTime.getFullYear();
      const endMonth = (endDateTime.getMonth() + 1).toString().padStart(2, '0');
      const endDay = endDateTime.getDate().toString().padStart(2, '0');
      const endHours = endDateTime.getHours().toString().padStart(2, '0');
      const endMinutes = endDateTime.getMinutes().toString().padStart(2, '0');
      const endDateTimeStr = `${endYear}-${endMonth}-${endDay}T${endHours}:${endMinutes}:00`;

      console.log('Creating event:', {
        date: meetingDate,
        time: meetingTime,
        startDateTimeStr,
        endDateTimeStr,
        timezone: userTimezone
      });

      const participantList = participants.trim() 
        ? participants.split(',').map(email => ({
            email: email.trim(),
            name: email.trim().split('@')[0]
          }))
        : [];

      await createEvent({
        slot: {
          start: startDateTimeStr,
          end: endDateTimeStr,
          score: 1.0
        },
        title: meetingTitle,
        description: description || `Meeting scheduled for ${duration} minutes`,
        participants: participantList,
      });

      setSuccess("Meeting created successfully! Check your Google Calendar.");
      
      // Reset form
      setTimeout(() => {
        setMeetingTitle("");
        setDescription("");
        setParticipants("");
        setMeetingTime("");
        setDaySlots([]);
        setSuccess("");
      }, 5000);
    } catch (err: any) {
      console.error("Error details:", err.response?.data);
      const errorMsg = err.response?.data?.detail 
        ? (typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : JSON.stringify(err.response.data.detail))
        : "Failed to create event";
      setError(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };



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
                SmartMeet
              </h1>
            </div>
            <div className="flex gap-3">
              <button
                onClick={() => router.push("/schedule")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                📅 Today's Schedule
              </button>
              <button
                onClick={() => router.push("/meetings")}
                className="px-4 py-2 text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors font-medium"
              >
                📋 History
              </button>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-gray-700 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium"
              >
                🚪 Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Timezone Display */}
        <div className="mb-6 flex items-center justify-center">
          <div className="bg-white px-4 py-2 rounded-full shadow-sm border border-gray-200">
            <span className="text-sm text-gray-600">🌍 Your timezone: </span>
            <span className="text-sm font-semibold text-gray-900">{getTimezoneDisplay()}</span>
          </div>
        </div>

        {/* Input Form */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
          <div className="flex items-center space-x-3 mb-6">
            <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center">
              <span className="text-2xl">✨</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900">
              Schedule a Meeting
            </h2>
          </div>
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Meeting Title */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Meeting Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={meetingTitle}
                onChange={(e) => setMeetingTitle(e.target.value)}
                placeholder="e.g., Team Sync, Project Review"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                disabled={isLoading}
                required
              />
            </div>

            {/* Date and Duration Row */}
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  value={meetingDate}
                  onChange={(e) => setMeetingDate(e.target.value)}
                  min={format(new Date(), "yyyy-MM-dd")}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  disabled={isLoading}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Duration (minutes)
                </label>
                <select
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                  disabled={isLoading}
                >
                  <option value="15">15 min</option>
                  <option value="30">30 min</option>
                  <option value="45">45 min</option>
                  <option value="60">1 hour</option>
                  <option value="90">1.5 hours</option>
                  <option value="120">2 hours</option>
                </select>
              </div>
            </div>

            {/* Participants */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Participants (emails) <span className="text-gray-400">(optional)</span>
              </label>
              <input
                type="text"
                value={participants}
                onChange={(e) => setParticipants(e.target.value)}
                placeholder="alice@example.com, bob@example.com"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">Separate multiple emails with commas (leave empty for personal meeting)</p>
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Description (optional)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add meeting agenda or notes..."
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none text-gray-900"
                rows={3}
                disabled={isLoading}
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed font-semibold shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Checking Availability...
                </span>
              ) : (
                "🔍 Check Availability"
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border-2 border-red-200 text-red-700 px-6 py-4 rounded-xl mb-8 flex items-start space-x-3 shadow-sm">
            <span className="text-2xl">⚠️</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Notice</p>
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="bg-green-50 border-2 border-green-200 text-green-700 px-6 py-4 rounded-xl mb-8 flex items-start space-x-3 shadow-sm">
            <span className="text-2xl">✅</span>
            <div className="flex-1">
              <p className="font-semibold mb-1">Success!</p>
              <p className="text-sm">{success}</p>
            </div>
          </div>
        )}

        {/* Event Details Modal */}
        {selectedBusySlot && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-2xl font-bold text-gray-900">
                    Scheduled Events
                  </h3>
                  <button
                    onClick={() => setSelectedBusySlot(null)}
                    className="text-gray-400 hover:text-gray-600 text-2xl"
                  >
                    ×
                  </button>
                </div>
                
                <div className="mb-4 space-y-2">
                  {selectedBusySlot.status === "partial" ? (
                    <>
                      <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <p className="text-sm text-yellow-700 font-semibold">
                          🟡 Partially Busy - {selectedBusySlot.free_minutes} minutes available
                        </p>
                        <p className="text-xs text-yellow-600 mt-1">
                          Busy: {selectedBusySlot.busy_minutes} min | Free: {selectedBusySlot.free_minutes} min
                        </p>
                      </div>
                      
                      {selectedBusySlot.free_periods && selectedBusySlot.free_periods.length > 0 && (
                        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-sm text-green-700 font-semibold mb-2">
                            ✅ Available Time Periods:
                          </p>
                          <div className="space-y-1">
                            {selectedBusySlot.free_periods.map((period: any, idx: number) => (
                              <div key={idx} className="text-xs text-green-600 flex items-center justify-between">
                                <span>
                                  {format(new Date(period.start), "h:mm a")} - {format(new Date(period.end), "h:mm a")}
                                </span>
                                <span className="font-semibold">
                                  ({period.duration_minutes} min)
                                </span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-700">
                        🔴 This time slot is fully busy
                      </p>
                    </div>
                  )}
                </div>

                {selectedBusySlot.events && selectedBusySlot.events.length > 0 ? (
                  <div className="space-y-4">
                    {selectedBusySlot.events.map((event: any, idx: number) => (
                      <div key={idx} className="border-2 border-gray-200 rounded-xl p-4">
                        <h4 className="font-bold text-lg text-gray-900 mb-2">
                          {event.title}
                        </h4>
                        
                        {event.description && (
                          <div className="mb-3">
                            <p className="text-sm font-semibold text-gray-700 mb-1">Description:</p>
                            <p className="text-sm text-gray-600">{event.description}</p>
                          </div>
                        )}
                        
                        <div className="grid md:grid-cols-2 gap-3 text-sm">
                          <div>
                            <p className="font-semibold text-gray-700">Start:</p>
                            <p className="text-gray-600">
                              {event.start ? format(new Date(event.start), "MMM d, yyyy 'at' h:mm a") : "N/A"}
                            </p>
                          </div>
                          <div>
                            <p className="font-semibold text-gray-700">End:</p>
                            <p className="text-gray-600">
                              {event.end ? format(new Date(event.end), "MMM d, yyyy 'at' h:mm a") : "N/A"}
                            </p>
                          </div>
                        </div>

                        {event.attendees && event.attendees.length > 0 && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-700 mb-1">Attendees:</p>
                            <div className="flex flex-wrap gap-2">
                              {event.attendees.map((email: string, i: number) => (
                                <span key={i} className="bg-blue-100 text-blue-700 px-2 py-1 rounded-full text-xs">
                                  {email}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {event.location && (
                          <div className="mt-3">
                            <p className="text-sm font-semibold text-gray-700">Location:</p>
                            <p className="text-sm text-gray-600">{event.location}</p>
                          </div>
                        )}

                        <div className="mt-3 flex items-center justify-between">
                          {event.htmlLink && (
                            <a
                              href={event.htmlLink}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-800 underline"
                            >
                              View in Google Calendar →
                            </a>
                          )}
                          <button
                            onClick={() => handleDeleteEvent(event.id)}
                            disabled={deletingEventId === event.id}
                            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm font-semibold transition-colors"
                          >
                            {deletingEventId === event.id ? (
                              <span className="flex items-center">
                                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                Deleting...
                              </span>
                            ) : (
                              "🗑️ Delete Event"
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-600">No event details available.</p>
                )}

                <div className="mt-6 space-y-3">
                  {selectedBusySlot.status === "partial" && selectedBusySlot.free_minutes >= parseInt(duration) && (
                    <button
                      onClick={() => {
                        const slotTime = new Date(selectedBusySlot.start);
                        const slotTimeStr = format(slotTime, "HH:mm");
                        setMeetingTime(slotTimeStr);
                        setSelectedBusySlot(null);
                      }}
                      className="w-full px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 font-semibold"
                    >
                      ✅ Schedule in Free Time ({selectedBusySlot.free_minutes} min available)
                    </button>
                  )}
                  {selectedBusySlot.status === "partial" && selectedBusySlot.free_minutes < parseInt(duration) && (
                    <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                      <p className="text-sm text-orange-700">
                        ⚠️ Not enough free time. Need {duration} min but only {selectedBusySlot.free_minutes} min available.
                      </p>
                    </div>
                  )}
                  <button
                    onClick={() => setSelectedBusySlot(null)}
                    className="w-full px-6 py-3 bg-gray-600 text-white rounded-xl hover:bg-gray-700 font-semibold"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Available Time Slots - Calendar Based */}
        {daySlots.length > 0 && (
          <div className="bg-white rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
            <div className="flex items-center space-x-3 mb-6">
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-xl">📅</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900">
                Available Time Slots
              </h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">
              🔴 Red = Fully Busy | 🟡 Yellow = Partially Busy | 🟢 Green = Available (9 AM - 6 PM)
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {daySlots.map((slot, index) => {
                const slotTime = new Date(slot.start);
                const hour = slotTime.getHours();
                const hourLabel = hour === 12 ? "12 PM" : hour > 12 ? `${hour - 12} PM` : `${hour} AM`;
                const status = slot.status || (slot.is_busy ? "busy" : "available");
                const slotTimeStr = format(slotTime, "HH:mm");
                const isSelected = meetingTime === slotTimeStr;
                
                // Determine colors based on status
                let borderColor, bgColor, iconBg, icon, statusText;
                if (isSelected) {
                  borderColor = "border-blue-500";
                  bgColor = "bg-blue-100";
                  iconBg = "bg-blue-600";
                  icon = "✓";
                  statusText = "Selected";
                } else if (status === "busy") {
                  borderColor = "border-red-300";
                  bgColor = "bg-red-50";
                  iconBg = "bg-red-500";
                  icon = "🔴";
                  statusText = "Busy";
                } else if (status === "partial") {
                  borderColor = "border-yellow-300";
                  bgColor = "bg-yellow-50";
                  iconBg = "bg-yellow-500";
                  icon = "🟡";
                  statusText = `${slot.free_minutes}min free`;
                } else {
                  borderColor = "border-green-300";
                  bgColor = "bg-green-50";
                  iconBg = "bg-green-500";
                  icon = "🟢";
                  statusText = "Available";
                }
                
                return (
                  <div
                    key={index}
                    onClick={() => {
                      if (status === "busy" || status === "partial") {
                        setSelectedBusySlot(slot);
                      } else {
                        setMeetingTime(slotTimeStr);
                      }
                    }}
                    className={`p-4 border-2 rounded-xl transition-all cursor-pointer ${borderColor} ${bgColor} hover:shadow-md ${
                      isSelected ? "shadow-lg" : ""
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-bold ${iconBg} text-white`}>
                          {icon}
                        </div>
                        <div>
                          <p className="font-bold text-gray-900">{hourLabel}</p>
                          <p className="text-xs text-gray-600">{statusText}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-gray-500 mt-4 text-center">
              💡 Click on a green slot to select that time. Selected slot will turn blue with a checkmark.
            </p>
            
            {/* Confirm Button */}
            {meetingTime && (
              <div className="mt-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
                <p className="text-sm text-blue-700 mb-3 text-center">
                  ✓ Time selected: <span className="font-bold">{meetingTime}</span>
                </p>
                <button
                  onClick={handleConfirm}
                  disabled={isLoading}
                  className="w-full px-8 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed font-bold text-lg shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5"
                >
                  {isLoading ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating Event...
                    </span>
                  ) : (
                    `✅ Create Meeting`
                  )}
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
