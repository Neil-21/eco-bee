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
    const circumference = 2 * Math.PI * 35; // radius of 35 to match the circle
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

  // Get progress bar width class
  const getProgressBarClass = (value: number) => {
    const width = Math.max(5, 100 - value);
    if (width >= 90) return "w-full";
    if (width >= 80) return "w-5/6";
    if (width >= 75) return "w-3/4";
    if (width >= 60) return "w-3/5";
    if (width >= 50) return "w-1/2";
    if (width >= 40) return "w-2/5";
    if (width >= 33) return "w-1/3";
    if (width >= 25) return "w-1/4";
    if (width >= 20) return "w-1/5";
    if (width >= 16) return "w-1/6";
    return "w-1/12";
  };

  return (
    <div className="max-w-4xl mx-auto bg-white shadow-xl rounded-2xl overflow-hidden relative">
      {/* Fixed Floating Score Circle - Top Right */}
      <div className="fixed top-4 right-4 z-50 bg-white rounded-full shadow-lg p-2">
        <div className="relative">
          <svg className="w-20 h-20 transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r="35"
              stroke="#e5e7eb"
              strokeWidth="6"
              fill="none"
            />
            {/* Score circle */}
            <circle
              cx="50"
              cy="50"
              r="35"
              stroke={
                scoringResult.composite <= 30
                  ? "#10b981"
                  : scoringResult.composite <= 60
                  ? "#f59e0b"
                  : "#ef4444"
              }
              strokeWidth="6"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={
                createRadialScore(100 - scoringResult.composite).strokeDasharray
              }
              strokeDashoffset={
                createRadialScore(100 - scoringResult.composite)
                  .strokeDashoffset
              }
              className="transition-all duration-1000"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center flex-col">
            <div
              className={`text-sm font-bold ${getScoreColor(
                scoringResult.composite
              )}`}
            >
              {Math.round(100 - scoringResult.composite)}
            </div>
            <div
              className={`text-xs font-bold px-1 py-0.5 rounded-full ${getGradeColor(
                scoringResult.grade
              )}`}
            >
              {scoringResult.grade}
            </div>
          </div>
        </div>
      </div>

      {/* Header */}
      <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-4 text-center">
        <FaTrophy className="mx-auto text-3xl mb-2 opacity-90" />
        <h1 className="text-2xl font-bold mb-1">Your EcoBee Score</h1>
        <p className="text-green-100 text-sm">
          Environmental Impact Assessment
        </p>
      </div>

      {/* Boundary Breakdown */}
      <div className="py-2 px-3 border-b border-gray-200">
        <h2 className="text-lg font-bold text-gray-800 mb-2 flex items-center">
          <FaGlobe className="mr-2 text-blue-600" />
          Planetary Boundary Breakdown
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {boundaryScores.map(({ key, value, icon: Icon, color, bg, name }) => (
            <div key={key} className={`p-3 rounded-xl ${bg} border`}>
              <div className="flex items-center justify-between mb-1">
                <Icon className={`text-xl ${color}`} />
                <span className={`text-xl font-bold ${getScoreColor(value)}`}>
                  {Math.round(100 - value)}
                </span>
              </div>
              <h3 className="font-semibold text-gray-800 text-xs">{name}</h3>
              <div className="mt-1 bg-gray-200 rounded-full h-1.5 overflow-hidden">
                <div
                  className={`h-1.5 rounded-full transition-all duration-500 ${
                    value <= 30
                      ? "bg-green-500"
                      : value <= 60
                      ? "bg-yellow-500"
                      : "bg-red-500"
                  } ${getProgressBarClass(value)}`}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recommendations */}
      {scoringResult.recommendations &&
        scoringResult.recommendations.length > 0 && (
          <div className="py-2 px-3 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800 mb-2 flex items-center">
              <FaLightbulb className="mr-2 text-yellow-500" />
              Your Top Improvement Actions
            </h2>

            <div className="space-y-2">
              {scoringResult.recommendations.slice(0, 3).map((rec, index) => (
                <div
                  key={index}
                  className="bg-gradient-to-r from-blue-50 to-green-50 border border-blue-200 rounded-xl p-3"
                >
                  <div className="flex items-start space-x-3">
                    <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center font-bold text-sm">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-bold text-gray-800 text-base mb-1">
                        {rec.action}
                      </h3>
                      <p className="text-gray-600 mb-1 text-sm">{rec.impact}</p>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs text-blue-600 bg-blue-100 px-2 py-0.5 rounded-full">
                          {rec.boundary}
                        </span>
                        <span className="text-xs text-gray-500">
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
      <div className="py-2 px-3 bg-gray-50">
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleShare}
            className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <FaShareAlt />
            <span>Share Results</span>
          </button>

          <button
            onClick={onRestart}
            className="flex items-center justify-center space-x-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
          >
            <FaArrowLeft />
            <span>Take Again</span>
          </button>

          {onGetTips && (
            <button
              onClick={onGetTips}
              className="flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
            >
              <FaComments />
              <span>Get Personalized Tips</span>
            </button>
          )}

          {onNext && (
            <button
              onClick={onNext}
              className="flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
            >
              <span>View Leaderboard</span>
              <FaArrowRight />
            </button>
          )}
        </div>

        <div className="text-center mt-3">
          <p className="text-xs text-gray-500">
            Want to improve your score? Check back regularly and track your
            progress!
          </p>
        </div>
      </div>
    </div>
  );
}
