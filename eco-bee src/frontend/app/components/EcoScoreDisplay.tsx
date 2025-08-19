"use client";
import React from "react";
import { useRouter } from "next/navigation";
import {
  FaLeaf,
  FaGlobe,
  FaWater,
  FaWind,
  FaRecycle,
  FaArrowRight,
  FaArrowLeft,
  FaTrophy,
  FaLightbulb,
  FaShareAlt,
  FaComments,
} from "react-icons/fa";

interface BoundaryScore {
  climate: number;
  biosphere: number;
  biogeochemical: number;
  freshwater: number;
  aerosols: number;
}

interface Recommendation {
  action: string;
  impact: string;
  boundary: string;
  current_score: number;
}

interface ScoringResult {
  items: any[];
  per_boundary_averages: BoundaryScore;
  composite: number;
  grade: string;
  recommendations: Recommendation[];
  boundary_details: any;
}

interface EcoScoreDisplayProps {
  scoringResult: ScoringResult;
  onRestart: () => void;
  onNext?: () => void;
  onGetTips?: () => void;
}

const BOUNDARY_ICONS = {
  climate: {
    icon: FaGlobe,
    color: "text-red-500",
    bg: "bg-red-100",
    name: "Climate Change",
  },
  biosphere: {
    icon: FaLeaf,
    color: "text-green-500",
    bg: "bg-green-100",
    name: "Biosphere Integrity",
  },
  biogeochemical: {
    icon: FaRecycle,
    color: "text-blue-500",
    bg: "bg-blue-100",
    name: "Biogeochemical Flows",
  },
  freshwater: {
    icon: FaWater,
    color: "text-cyan-500",
    bg: "bg-cyan-100",
    name: "Freshwater Use",
  },
  aerosols: {
    icon: FaWind,
    color: "text-gray-500",
    bg: "bg-gray-100",
    name: "Aerosols & Novel Entities",
  },
};

const getGradeColor = (grade: string) => {
  switch (grade) {
    case "A+":
    case "A":
      return "text-green-600 bg-green-100";
    case "B+":
    case "B":
      return "text-blue-600 bg-blue-100";
    case "C+":
    case "C":
      return "text-yellow-600 bg-yellow-100";
    case "D":
      return "text-orange-600 bg-orange-100";
    default:
      return "text-red-600 bg-red-100";
  }
};

const getScoreColor = (score: number) => {
  if (score <= 30) return "text-green-600";
  if (score <= 50) return "text-yellow-600";
  if (score <= 70) return "text-orange-600";
  return "text-red-600";
};

export default function EcoScoreDisplay({
  scoringResult,
  onRestart,
  onNext,
  onGetTips,
}: EcoScoreDisplayProps) {
  const router = useRouter();

  const boundaryScores = Object.entries(
    scoringResult.per_boundary_averages
  ).map(([key, value]) => ({
    key,
    value: Math.round(value),
    ...BOUNDARY_ICONS[key as keyof typeof BOUNDARY_ICONS],
  }));

  const createRadialScore = (score: number) => {
    const circumference = 2 * Math.PI * 45; // radius of 45
    const strokeDasharray = circumference;
    const strokeDashoffset = circumference - (score / 100) * circumference;

    return { strokeDasharray, strokeDashoffset };
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: "My EcoBee Environmental Score",
        text: `I scored ${scoringResult.grade} (${scoringResult.composite}/100) on my environmental impact assessment!`,
        url: window.location.href,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(
        `I scored ${scoringResult.grade} (${scoringResult.composite}/100) on my environmental impact assessment! Check out EcoBee: ${window.location.href}`
      );
      alert("Score copied to clipboard!");
    }
  };

  return (
    <div className="max-w-4xl mx-auto bg-white shadow-xl rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-8 text-center">
        <FaTrophy className="mx-auto text-4xl mb-4 opacity-90" />
        <h1 className="text-3xl font-bold mb-2">Your EcoBee Score</h1>
        <p className="text-green-100">Environmental Impact Assessment</p>
      </div>

      {/* Main Score */}
      <div className="p-8 text-center border-b border-gray-200">
        <div className="relative inline-block mb-6">
          <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="#e5e7eb"
              strokeWidth="8"
              fill="none"
            />
            {/* Score circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke={
                scoringResult.composite <= 30
                  ? "#10b981"
                  : scoringResult.composite <= 60
                  ? "#f59e0b"
                  : "#ef4444"
              }
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              style={createRadialScore(100 - scoringResult.composite)} // Invert for better display
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <div
              className={`text-4xl font-bold ${getScoreColor(
                scoringResult.composite
              )}`}
            >
              {Math.round(100 - scoringResult.composite)}/100
            </div>
            <div
              className={`text-2xl font-bold px-3 py-1 rounded-full ${getGradeColor(
                scoringResult.grade
              )}`}
            >
              {scoringResult.grade}
            </div>
          </div>
        </div>

        <p className="text-lg text-gray-600 max-w-md mx-auto">
          {scoringResult.composite <= 30
            ? "Excellent! You're living within planetary boundaries."
            : scoringResult.composite <= 60
            ? "Good progress! There's room for improvement."
            : "Your lifestyle has significant environmental impact. Let's make some changes!"}
        </p>
      </div>

      {/* Boundary Breakdown */}
      <div className="p-8 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <FaGlobe className="mr-3 text-blue-600" />
          Planetary Boundary Breakdown
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {boundaryScores.map(({ key, value, icon: Icon, color, bg, name }) => (
            <div key={key} className={`p-4 rounded-xl ${bg} border`}>
              <div className="flex items-center justify-between mb-2">
                <Icon className={`text-2xl ${color}`} />
                <span className={`text-2xl font-bold ${getScoreColor(value)}`}>
                  {Math.round(100 - value)}
                </span>
              </div>
              <h3 className="font-semibold text-gray-800 text-sm">{name}</h3>
              <div className="mt-2 bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    value <= 30
                      ? "bg-green-500"
                      : value <= 60
                      ? "bg-yellow-500"
                      : "bg-red-500"
                  }`}
                  style={{ width: `${Math.max(5, 100 - value)}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {scoringResult.recommendations &&
        scoringResult.recommendations.length > 0 && (
          <div className="p-8 border-b border-gray-200">
            <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
              <FaLightbulb className="mr-3 text-yellow-500" />
              Your Top Improvement Actions
            </h2>

            <div className="space-y-4">
              {scoringResult.recommendations.slice(0, 3).map((rec, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-xl p-6"
                >
                  <div className="flex items-start space-x-4">
                    <div className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center font-bold">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-800 text-lg mb-2">
                        {rec.action}
                      </h3>
                      <p className="text-gray-600 mb-2">{rec.impact}</p>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-blue-600 bg-blue-100 px-2 py-1 rounded-full">
                          {rec.boundary}
                        </span>
                        <span className="text-sm text-gray-500">
                          Current score: {Math.round(100 - rec.current_score)}
                          /100
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      {/* Action Buttons */}
      <div className="p-8 bg-gray-50">
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button
            onClick={handleShare}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <FaShareAlt />
            <span>Share Results</span>
          </button>

          <button
            onClick={onRestart}
            className="flex items-center justify-center space-x-2 px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
          >
            <FaArrowLeft />
            <span>Take Again</span>
          </button>

          {onGetTips && (
            <button
              onClick={onGetTips}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <FaComments />
              <span>Get Personalized Tips</span>
            </button>
          )}

          {onNext && (
            <button
              onClick={onNext}
              className="flex items-center justify-center space-x-2 px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              <span>View Leaderboard</span>
              <FaArrowRight />
            </button>
          )}
        </div>

        <div className="text-center mt-6">
          <p className="text-sm text-gray-500">
            Want to improve your score? Check back regularly and track your
            progress!
          </p>
        </div>
      </div>
    </div>
  );
}
