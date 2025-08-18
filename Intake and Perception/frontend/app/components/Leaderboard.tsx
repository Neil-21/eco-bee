"use client";
import React, { useState, useEffect } from "react";
import {
  FaTrophy,
  FaMedal,
  FaAward,
  FaArrowLeft,
  FaLeaf,
} from "react-icons/fa";

interface LeaderboardEntry {
  rank?: number;
  user_id?: string;
  composite_score?: number;
  grade?: string;
  campus_affiliation?: string;
  timestamp?: string;
  boundary_scores?: {
    climate: number;
    biosphere: number;
    biogeochemical: number;
    freshwater: number;
    aerosols: number;
  };
}

interface LeaderboardProps {
  onBack: () => void;
}

export default function Leaderboard({ onBack }: LeaderboardProps) {
  const [leaderboardData, setLeaderboardData] = useState<LeaderboardEntry[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        "http://localhost:8000/api/leaderboard?limit=50"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch leaderboard");
      }

      const data = await response.json();
      setLeaderboardData(data.leaderboard || []);
    } catch (error) {
      console.error("Error fetching leaderboard:", error);
      setError("Failed to load leaderboard data");
    } finally {
      setLoading(false);
    }
  };

  const getRankIcon = (rank: number) => {
    switch (rank) {
      case 1:
        return <FaTrophy className="text-yellow-500 text-2xl" />;
      case 2:
        return <FaMedal className="text-gray-400 text-2xl" />;
      case 3:
        return <FaAward className="text-orange-500 text-2xl" />;
      default:
        return (
          <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
            <span className="text-green-600 font-bold text-sm">{rank}</span>
          </div>
        );
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case "A":
        return "text-green-600 bg-green-100";
      case "B":
        return "text-blue-600 bg-blue-100";
      case "C":
        return "text-yellow-600 bg-yellow-100";
      case "D":
        return "text-orange-600 bg-orange-100";
      case "F":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading leaderboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center">
        <div className="max-w-md mx-auto bg-white shadow-xl rounded-2xl p-8 text-center">
          <div className="text-red-500 text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            Error Loading Leaderboard
          </h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={onBack}
            className="bg-green-500 text-white px-6 py-2 rounded-lg hover:bg-green-600 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 p-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white shadow-xl rounded-2xl mb-6 overflow-hidden">
          <div className="bg-gradient-to-r from-yellow-500 to-orange-600 text-white p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <button
                  onClick={onBack}
                  className="text-yellow-100 hover:text-white transition-colors"
                  title="Go back to home"
                  aria-label="Go back to home"
                >
                  <FaArrowLeft className="text-xl" />
                </button>
                <div>
                  <h1 className="text-3xl font-bold flex items-center">
                    <FaTrophy className="mr-3" />
                    EcoLeaderboard
                  </h1>
                  <p className="text-yellow-100">
                    See how EcoBee users are making a difference
                  </p>
                </div>
              </div>
              <FaLeaf className="text-5xl text-yellow-200 opacity-50" />
            </div>
          </div>

          {/* Stats */}
          <div className="p-6 bg-gradient-to-r from-yellow-50 to-orange-50">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-800">
                  {leaderboardData.length}
                </div>
                <div className="text-sm text-gray-600">Total Participants</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {leaderboardData.length > 0
                    ? Math.round(
                        leaderboardData.reduce(
                          (sum, entry) => sum + (entry.composite_score || 0),
                          0
                        ) / leaderboardData.length
                      )
                    : 0}
                </div>
                <div className="text-sm text-gray-600">Average Score</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {
                    leaderboardData.filter((entry) => entry.grade === "A")
                      .length
                  }
                </div>
                <div className="text-sm text-gray-600">A-Grade Eco Heroes</div>
              </div>
            </div>
          </div>
        </div>

        {/* Leaderboard */}
        <div className="bg-white shadow-xl rounded-2xl overflow-hidden">
          <div className="p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Top Performers
            </h2>

            {leaderboardData.length === 0 ? (
              <div className="text-center py-8">
                <FaLeaf className="text-gray-300 text-4xl mx-auto mb-4" />
                <p className="text-gray-500">
                  No leaderboard data available yet.
                </p>
                <p className="text-gray-400 text-sm">
                  Be the first to take the quiz and appear here!
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {leaderboardData.slice(0, 20).map((entry, index) => (
                  <div
                    key={entry.user_id || `entry-${index}`}
                    className={`flex items-center justify-between p-4 rounded-xl transition-all duration-200 hover:shadow-md ${
                      index < 3
                        ? "bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200"
                        : "bg-gray-50 hover:bg-gray-100"
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      {getRankIcon(entry.rank || index + 1)}
                      <div>
                        <div className="font-semibold text-gray-800">
                          User #
                          {entry.user_id
                            ? entry.user_id.substring(0, 8)
                            : "Anonymous"}
                          ...
                        </div>
                        {entry.campus_affiliation && (
                          <div className="text-sm text-gray-600">
                            {entry.campus_affiliation}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-lg font-bold text-gray-800">
                          {entry.composite_score || 0}
                        </div>
                        <div className="text-sm text-gray-600">EcoScore</div>
                      </div>
                      <div
                        className={`px-3 py-1 rounded-full text-sm font-bold ${getGradeColor(
                          entry.grade || "N/A"
                        )}`}
                      >
                        {entry.grade || "N/A"}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Back Button */}
        <div className="text-center mt-6">
          <button
            onClick={onBack}
            className="bg-green-500 text-white px-8 py-3 rounded-xl font-semibold hover:bg-green-600 transition-colors shadow-lg"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  );
}
