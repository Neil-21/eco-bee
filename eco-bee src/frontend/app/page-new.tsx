"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import ChatInterface from "./components/ChatInterface";
import EcoScoreDisplay from "./components/EcoScoreDisplay";
import { QuizResponse } from "./types/quiz";
import {
  FaLeaf,
  FaGlobe,
  FaHeart,
  FaUsers,
  FaPlay,
  FaArrowRight,
} from "react-icons/fa";

type AppState = "landing" | "chat" | "results" | "leaderboard";

interface ScoringResult {
  items: any[];
  per_boundary_averages: {
    climate: number;
    biosphere: number;
    biogeochemical: number;
    freshwater: number;
    aerosols: number;
  };
  composite: number;
  grade: string;
  recommendations: Array<{
    action: string;
    impact: string;
    boundary: string;
    current_score: number;
  }>;
  boundary_details: any;
}

export default function EcoBeeLanding() {
  const router = useRouter();
  const [appState, setAppState] = useState<AppState>("landing");
  const [sessionData, setSessionData] = useState<any>(null);
  const [scoringResult, setScoringResult] = useState<ScoringResult | null>(
    null
  );

  const handleStartExperience = () => {
    setAppState("chat");
  };

  const handleChatComplete = async (data: any) => {
    setSessionData(data);

    // Process the chat data and get EcoScore
    try {
      // This would normally call the backend API with the session data
      // For now, we'll simulate the API call

      const mockItems = [
        {
          type: "meal",
          category: data.question_1?.includes("Plant")
            ? "plant-based"
            : data.question_1?.includes("Meat")
            ? "meat-heavy"
            : "mixed",
          materials: ["food"],
          confidence: 0.9,
          source: "quiz",
        },
        {
          type: "transport",
          category: data.question_2?.includes("Walking")
            ? "walk"
            : data.question_2?.includes("Cycling")
            ? "bike"
            : data.question_2?.includes("Public")
            ? "bus"
            : "car",
          materials: ["transport"],
          confidence: 0.9,
          source: "quiz",
        },
      ];

      const response = await fetch("http://localhost:8000/api/intake", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          quiz_responses: [],
          items: mockItems,
          session_id: Date.now().toString(),
          user_id: `user_${Date.now()}`,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setScoringResult(result.scoring_result);
        setAppState("results");
      } else {
        console.error("Failed to get EcoScore");
        // Show mock results as fallback
        showMockResults();
      }
    } catch (error) {
      console.error("Error calling API:", error);
      // Show mock results as fallback
      showMockResults();
    }
  };

  const showMockResults = () => {
    const mockResult: ScoringResult = {
      items: [],
      per_boundary_averages: {
        climate: 58,
        biosphere: 45,
        biogeochemical: 55,
        freshwater: 68,
        aerosols: 52,
      },
      composite: 55.6,
      grade: "C+",
      recommendations: [
        {
          action: "Switch to plant-based meals 3 days/week",
          impact: "Reduce climate impact by 25%",
          boundary: "Climate Change",
          current_score: 58,
        },
        {
          action: "Use public transport or bike for short trips",
          impact: "Reduce emissions and pollution",
          boundary: "Atmospheric Aerosol Loading",
          current_score: 52,
        },
        {
          action: "Choose water-efficient food options",
          impact: "Reduce freshwater pressure by 20%",
          boundary: "Freshwater Use",
          current_score: 68,
        },
      ],
      boundary_details: {},
    };
    setScoringResult(mockResult);
    setAppState("results");
  };

  const handleRestart = () => {
    setAppState("landing");
    setSessionData(null);
    setScoringResult(null);
  };

  const handleViewLeaderboard = () => {
    setAppState("leaderboard");
  };

  if (appState === "chat") {
    return <ChatInterface onComplete={handleChatComplete} />;
  }

  if (appState === "results" && scoringResult) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-yellow-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-green-800 mb-4">
                🎉 Your EcoBee Results!
              </h1>
              <p className="text-lg text-gray-600">
                Here's your complete planetary impact assessment
              </p>
            </div>

            <EcoScoreDisplay
              scoringResult={scoringResult}
              onRestart={handleRestart}
              onNext={handleViewLeaderboard}
            />

            <div className="mt-8 text-center space-y-4">
              <button
                onClick={handleViewLeaderboard}
                className="px-8 py-3 bg-yellow-500 hover:bg-yellow-600 text-white rounded-lg font-semibold flex items-center gap-2 mx-auto transition-colors"
              >
                <FaUsers />
                See Campus Leaderboard
              </button>

              <button
                onClick={handleRestart}
                className="px-6 py-2 text-green-600 hover:text-green-700 underline"
              >
                Try Again with Different Answers
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (appState === "leaderboard") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-yellow-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-green-800 mb-4">
                🏆 Campus EcoScore Leaderboard
              </h1>
              <p className="text-lg text-gray-600">
                See how you compare with other students
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="text-center text-gray-600 py-8">
                <FaUsers className="text-4xl mx-auto mb-4 text-gray-400" />
                <p>Leaderboard data will be loaded here...</p>
                <p className="text-sm mt-2">
                  Connect to backend to see real rankings
                </p>
              </div>

              <div className="mt-6 text-center">
                <button
                  onClick={handleRestart}
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  Start New Assessment
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Landing page
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-yellow-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <div className="flex items-center justify-center gap-3 mb-6">
              <div className="text-6xl">🐝</div>
              <div className="text-left">
                <h1 className="text-5xl font-bold text-green-800">EcoBee</h1>
                <p className="text-xl text-green-600">
                  Personalised Sustainability Companion
                </p>
              </div>
            </div>

            <p className="text-xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
              Discover your <strong>EcoScore</strong> across Earth's planetary
              boundaries and get personalized recommendations to reduce your
              environmental impact. Join thousands of students creating positive
              change! 🌍
            </p>
          </div>

          {/* Value Propositions */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <FaGlobe className="text-3xl text-blue-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-800 mb-2">
                Science-Based
              </h3>
              <p className="text-sm text-gray-600">
                Uses the Planetary Boundaries framework from Stockholm
                Resilience Centre
              </p>
            </div>

            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <FaHeart className="text-3xl text-red-500 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-800 mb-2">Personalized</h3>
              <p className="text-sm text-gray-600">
                Get recommendations tailored to your lifestyle and campus
                resources
              </p>
            </div>

            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <FaUsers className="text-3xl text-purple-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-800 mb-2">Community</h3>
              <p className="text-sm text-gray-600">
                Compare with peers and discover campus sustainability
                opportunities
              </p>
            </div>

            <div className="text-center p-6 bg-white rounded-lg shadow-sm">
              <FaLeaf className="text-3xl text-green-600 mx-auto mb-3" />
              <h3 className="font-semibold text-gray-800 mb-2">Actionable</h3>
              <p className="text-sm text-gray-600">
                Get specific actions you can take today to make a real
                difference
              </p>
            </div>
          </div>

          {/* How It Works */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-12">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-8">
              How It Works
            </h2>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📝</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  5-Minute Assessment
                </h3>
                <p className="text-gray-600">
                  Quick questions about your food, transport, clothing, and
                  lifestyle choices
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">📊</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Get Your EcoScore
                </h3>
                <p className="text-gray-600">
                  See your impact across 5 planetary boundaries with a clear
                  0-100 score
                </p>
              </div>

              <div className="text-center">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">💡</span>
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">
                  Take Action
                </h3>
                <p className="text-gray-600">
                  Get personalized recommendations and connect with campus
                  resources
                </p>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="text-center">
            <div className="bg-gradient-to-r from-green-600 to-blue-600 rounded-lg p-8 text-white">
              <h2 className="text-3xl font-bold mb-4">
                Ready to Discover Your Impact?
              </h2>
              <p className="text-lg mb-6 opacity-90">
                Join thousands of students taking action for our planet's future
              </p>

              <button
                onClick={handleStartExperience}
                className="px-8 py-4 bg-white text-green-700 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors flex items-center gap-3 mx-auto"
              >
                <FaPlay />
                Start Your EcoScore Assessment
                <FaArrowRight />
              </button>

              <p className="text-sm mt-4 opacity-75">
                Takes about 5 minutes • Completely anonymous • No account
                required
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
