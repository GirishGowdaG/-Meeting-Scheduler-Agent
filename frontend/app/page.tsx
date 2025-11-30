"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem("token");
    if (token) {
      router.push("/app");
    }
  }, [router]);

  const handleGoogleLogin = async () => {
    console.log("Sign in button clicked");
    console.log("API URL:", API_URL);
    setIsLoading(true);
    try {
      console.log("Fetching auth URL from backend...");
      const response = await axios.get(`${API_URL}/auth/google/login`);
      console.log("Auth URL received:", response.data.auth_url);
      window.location.href = response.data.auth_url;
    } catch (error) {
      console.error("Failed to initiate login:", error);
      alert("Failed to connect to authentication server. Please check if the backend is running.");
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">SM</span>
              </div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                SmartMeet
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">Powered by AI</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4 py-16">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          <div className="text-center mb-20">
            <div className="inline-block mb-4">
              <span className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-semibold">
                ✨ AI-Powered Scheduling
              </span>
            </div>
            <h1 className="text-6xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Schedule Meetings
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                The Smart Way
              </span>
            </h1>
            <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto leading-relaxed">
              Just describe your meeting in plain English. Our AI finds the perfect time,
              checks calendars, and sends invites automatically.
            </p>

            {/* CTA Button */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <button
                onClick={handleGoogleLogin}
                disabled={isLoading}
                className="inline-flex items-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl hover:from-blue-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Connecting to Google...
                  </>
                ) : (
                  <>
                    <svg className="w-6 h-6 mr-3" viewBox="0 0 24 24">
                      <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                    Sign in with Google
                  </>
                )}
              </button>
            </div>

            {/* Demo Example */}
            <div className="max-w-2xl mx-auto mb-16">
              <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-full flex items-center justify-center">
                      <span className="text-white text-lg">💬</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-gray-500 text-sm mb-2">Try saying:</p>
                    <p className="text-gray-800 font-medium italic">
                      "Schedule a 30-minute sync with alice@example.com tomorrow afternoon"
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Features */}
          <div className="grid md:grid-cols-3 gap-8 mb-20">
            <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100 group">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-indigo-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-3xl">🗣️</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Natural Language</h3>
              <p className="text-gray-600 leading-relaxed">
                Just type what you need in plain English. No forms, no complicated interfaces.
              </p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100 group">
              <div className="w-14 h-14 bg-gradient-to-br from-purple-100 to-pink-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-3xl">🤖</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">AI-Powered</h3>
              <p className="text-gray-600 leading-relaxed">
                Google Gemini AI understands your intent and finds the best meeting times automatically.
              </p>
            </div>
            <div className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-shadow border border-gray-100 group">
              <div className="w-14 h-14 bg-gradient-to-br from-green-100 to-emerald-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-3xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold mb-3 text-gray-900">Instant Setup</h3>
              <p className="text-gray-600 leading-relaxed">
                Creates calendar events with Google Meet links and sends invites in seconds.
              </p>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-white rounded-3xl shadow-xl p-12 mb-20">
            <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">How It Works</h2>
            <div className="grid md:grid-cols-4 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">1</div>
                <h4 className="font-semibold mb-2 text-gray-900">Describe</h4>
                <p className="text-sm text-gray-600">Tell us about your meeting in natural language</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-indigo-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">2</div>
                <h4 className="font-semibold mb-2 text-gray-900">AI Analyzes</h4>
                <p className="text-sm text-gray-600">Our AI checks calendars and finds available slots</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-purple-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">3</div>
                <h4 className="font-semibold mb-2 text-gray-900">Choose Time</h4>
                <p className="text-sm text-gray-600">Pick from 2-3 smart suggestions</p>
              </div>
              <div className="text-center">
                <div className="w-16 h-16 bg-pink-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto mb-4">4</div>
                <h4 className="font-semibold mb-2 text-gray-900">Done!</h4>
                <p className="text-sm text-gray-600">Event created, invites sent automatically</p>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="text-center text-gray-600">
            <p className="text-sm">
              Powered by Google Calendar, Google Meet, and Google Gemini AI
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
