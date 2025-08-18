"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import EnhancedQuiz from "./components/EnhancedQuiz";
import EcoScoreDisplay from "./components/EcoScoreDisplay";
import Leaderboard from "./components/Leaderboard";
import SustainabilityChatbot from "./components/SustainabilityChatbot";
import UserInfoCollection from "./components/UserInfoCollection";
import { QuizResponse } from "./types/quiz";
import {
  FaLeaf,
  FaGlobe,
  FaHeart,
  FaUsers,
  FaTrophy,
  FaComments,
  FaRobot,
} from "react-icons/fa";

type AppState =
  | "welcome"
  | "quiz"
  | "userinfo"
  | "results"
  | "leaderboard"
  | "chatbot";

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

export default function Home() {
  const router = useRouter();
  const [appState, setAppState] = useState<AppState>("welcome");
  const [quizResponses, setQuizResponses] = useState<QuizResponse[]>([]);
  const [scoringResult, setScoringResult] = useState<ScoringResult | null>(
    null
  );
  const [userInfo, setUserInfo] = useState<{
    name: string;
    university: string;
    saveToLeaderboard: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(false);

  const handleQuizComplete = async (
    responses: QuizResponse[],
    items: any[]
  ) => {
    setLoading(true);
    setQuizResponses(responses);

    try {
      // Submit to backend for scoring
      const response = await fetch("http://localhost:8000/api/intake", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          quiz_responses: responses,
          items: items,
          session_id: generateSessionId(),
          user_id: null,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to submit quiz");
      }

      const result = await response.json();

      if (result.scoring_result) {
        setScoringResult(result.scoring_result);
        setAppState("userinfo");
      } else {
        console.error("No scoring result received");
        // Fallback: create mock result
        setScoringResult(createMockScoringResult(responses));
        setAppState("userinfo");
      }
    } catch (error) {
      console.error("Error submitting quiz:", error);
      // Fallback: create mock result
      setScoringResult(createMockScoringResult(responses));
      setAppState("userinfo");
    } finally {
      setLoading(false);
    }
  };

  const generateSessionId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  };

  const createMockScoringResult = (
    responses: QuizResponse[]
  ): ScoringResult => {
    // Simple scoring based on responses
    let totalScore = 50; // baseline

    responses.forEach((response) => {
      if (response.question_id === "food_today") {
        switch (response.answer) {
          case "plant-based":
            totalScore -= 20;
            break;
          case "mixed":
            totalScore -= 5;
            break;
          case "meat-heavy":
            totalScore += 15;
            break;
          case "packaged":
            totalScore += 10;
            break;
        }
      }
      if (response.question_id === "transport_today") {
        switch (response.answer) {
          case "walk":
          case "bike":
            totalScore -= 15;
            break;
          case "public":
            totalScore -= 5;
            break;
          case "electric":
            totalScore += 5;
            break;
          case "car":
            totalScore += 20;
            break;
        }
      }
    });

    totalScore = Math.max(0, Math.min(100, totalScore));

    const boundaryScores = {
      climate: totalScore + Math.random() * 10 - 5,
      biosphere: totalScore + Math.random() * 10 - 5,
      biogeochemical: totalScore + Math.random() * 10 - 5,
      freshwater: totalScore + Math.random() * 10 - 5,
      aerosols: totalScore + Math.random() * 10 - 5,
    };

    return {
      items: [],
      per_boundary_averages: boundaryScores,
      composite: totalScore,
      grade:
        totalScore <= 30
          ? "A"
          : totalScore <= 50
          ? "B"
          : totalScore <= 70
          ? "C"
          : "D",
      recommendations: [
        {
          action: "Choose more plant-based meals",
          impact: "Reduce climate impact by 50%",
          boundary: "Climate Change",
          current_score: boundaryScores.climate,
        },
        {
          action: "Use public transport or walk more",
          impact: "Lower your carbon footprint",
          boundary: "Climate Change",
          current_score: boundaryScores.climate,
        },
      ],
      boundary_details: {},
    };
  };

  const renderWelcome = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="max-w-2xl mx-auto bg-white shadow-2xl rounded-3xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-8 text-center">
          <div className="text-6xl mb-4">🐝</div>
          <h1 className="text-4xl font-bold mb-2">EcoBee</h1>
          <p className="text-green-100 text-lg">
            Your Environmental Impact Snapshot
          </p>
        </div>

        {/* Content */}
        <div className="p-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">
              Discover Your Impact on Planet Earth
            </h2>
            <p className="text-gray-600 text-lg leading-relaxed">
              Take our quick 5-7 question quiz to understand how your daily
              choices affect the planetary boundaries that keep Earth in a
              stable, habitable state.
            </p>
          </div>

          {/* Features */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="flex items-start space-x-3">
              <FaLeaf className="text-green-500 text-2xl mt-1" />
              <div>
                <h3 className="font-semibold text-gray-800">
                  Planetary Boundaries
                </h3>
                <p className="text-gray-600 text-sm">
                  Get scored across climate, biosphere, water, and more
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <FaGlobe className="text-blue-500 text-2xl mt-1" />
              <div>
                <h3 className="font-semibold text-gray-800">Science-Based</h3>
                <p className="text-gray-600 text-sm">
                  Based on the latest environmental research
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <FaHeart className="text-red-500 text-2xl mt-1" />
              <div>
                <h3 className="font-semibold text-gray-800">Personal Action</h3>
                <p className="text-gray-600 text-sm">
                  Get tailored recommendations for positive impact
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <FaUsers className="text-purple-500 text-2xl mt-1" />
              <div>
                <h3 className="font-semibold text-gray-800">Community</h3>
                <p className="text-gray-600 text-sm">
                  Compare your progress with others
                </p>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <button
              onClick={() => setAppState("quiz")}
              className="bg-gradient-to-r from-green-500 to-blue-600 text-white font-bold py-4 px-8 rounded-xl text-lg hover:from-green-600 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
            >
              Start Your Environmental Snapshot
            </button>
            <p className="text-gray-500 text-sm mt-4">
              Takes 3-5 minutes • Optional image capture • Privacy-focused
            </p>
          </div>

          {/* Additional Features */}
          <div className="mt-8 pt-6 border-t border-gray-200">
            <h3 className="text-center text-lg font-semibold text-gray-800 mb-4">
              Explore More EcoBee Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Leaderboard Link */}
              <button
                onClick={() => setAppState("leaderboard")}
                className="flex items-center justify-center space-x-3 p-4 bg-gradient-to-r from-yellow-100 to-orange-100 hover:from-yellow-200 hover:to-orange-200 rounded-xl border border-yellow-200 transition-all duration-200 hover:shadow-md"
              >
                <FaTrophy className="text-yellow-600 text-xl" />
                <div className="text-left">
                  <div className="font-semibold text-gray-800">
                    EcoLeaderboard
                  </div>
                  <div className="text-sm text-gray-600">See how you rank</div>
                </div>
              </button>

              {/* Sustainability Chatbot Link */}
              <button
                onClick={() => setAppState("chatbot")}
                className="flex items-center justify-center space-x-3 p-4 bg-gradient-to-r from-blue-100 to-purple-100 hover:from-blue-200 hover:to-purple-200 rounded-xl border border-blue-200 transition-all duration-200 hover:shadow-md"
              >
                <FaRobot className="text-blue-600 text-xl" />
                <div className="text-left">
                  <div className="font-semibold text-gray-800">
                    EcoChat Assistant
                  </div>
                  <div className="text-sm text-gray-600">
                    Get sustainability advice
                  </div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderQuiz = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-4">
      <EnhancedQuiz onComplete={handleQuizComplete} />
    </div>
  );

  const renderResults = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-4">
      {scoringResult && (
        <EcoScoreDisplay
          scoringResult={scoringResult}
          onRestart={() => {
            setAppState("welcome");
            setQuizResponses([]);
            setScoringResult(null);
          }}
          onNext={() => setAppState("leaderboard")}
        />
      )}
    </div>
  );

  const handleUserInfoSubmit = async (userData: {
    name: string;
    university: string;
    saveToLeaderboard: boolean;
  }) => {
    setLoading(true);
    setUserInfo(userData);

    try {
      if (userData.saveToLeaderboard && scoringResult) {
        // Submit to leaderboard
        const response = await fetch("http://localhost:8000/api/submit-score", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            user_id: generateSessionId(),
            pseudonym: userData.name,
            composite_score: scoringResult.composite,
            boundary_scores: scoringResult.per_boundary_averages,
            campus_affiliation: userData.university,
            quiz_responses: quizResponses,
          }),
        });

        if (!response.ok) {
          console.error("Failed to submit to leaderboard");
        } else {
          console.log("Successfully added to leaderboard");
        }
      }
    } catch (error) {
      console.error("Error submitting user info:", error);
    } finally {
      setLoading(false);
      setAppState("results");
    }
  };

  const handleUserInfoSkip = () => {
    setUserInfo({
      name: "",
      university: "",
      saveToLeaderboard: false,
    });
    setAppState("results");
  };

  const renderLoading = () => (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl p-8 shadow-xl text-center">
        <div className="text-6xl mb-4">🌱</div>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Calculating Your EcoScore
        </h2>
        <p className="text-gray-600 mb-6">
          Analyzing your responses across planetary boundaries...
        </p>
        <div className="flex items-center justify-center space-x-2">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
          <span className="text-gray-600">Please wait</span>
        </div>
      </div>
    </div>
  );

  if (loading) return renderLoading();

  switch (appState) {
    case "welcome":
      return renderWelcome();
    case "quiz":
      return renderQuiz();
    case "userinfo":
      return (
        <UserInfoCollection
          onSubmit={handleUserInfoSubmit}
          onSkip={handleUserInfoSkip}
          loading={loading}
        />
      );
    case "results":
      return renderResults();
    case "leaderboard":
      return <Leaderboard onBack={() => setAppState("welcome")} />;
    case "chatbot":
      return <SustainabilityChatbot onBack={() => setAppState("welcome")} />;
    default:
      return renderWelcome();
  }
}
