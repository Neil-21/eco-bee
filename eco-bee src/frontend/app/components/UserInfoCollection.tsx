"use client";
import React, { useState } from "react";
import {
  FaUser,
  FaUniversity,
  FaGlobeAmericas,
  FaCheck,
  FaTimes,
} from "react-icons/fa";

interface UserInfo {
  name: string;
  university: string;
  saveToLeaderboard: boolean;
}

interface UserInfoCollectionProps {
  onSubmit: (userInfo: UserInfo) => void;
  onSkip: () => void;
  loading?: boolean;
}

export default function UserInfoCollection({
  onSubmit,
  onSkip,
  loading = false,
}: UserInfoCollectionProps) {
  const [userInfo, setUserInfo] = useState<UserInfo>({
    name: "",
    university: "",
    saveToLeaderboard: true,
  });

  const [errors, setErrors] = useState<{
    name?: string;
    university?: string;
  }>({});

  const universityOptions = [
    //sourced from https://ukstudyoptions.com/a-z-list-of-uk-universities/
    "University of Aberdeen",
    "University of Abertay",
    "University of Aberystwyth",
    "Anglia Ruskin University",
    "Aston University",
    "Bangor University",
    "University of Bath",
    "Bath Spa University",
    "University of Bedfordshire",
    "University of Birmingham",
    "Birmingham City University",
    "University of Bolton",
    "Bournemouth University",
    "University of Bradford",
    "University of Brighton",
    "University of Bristol",
    "Brunel University",
    "University of Buckingham",
    "Buckinghamshire New University",
    "University of Cambridge",
    "Canterbury Christ Church University",
    "Cardiff University",
    "Cardiff University of Wales Institute (UWIC)",
    "University of Central Lancashire (UCLan)",
    "Chester University",
    "University of Chichester",
    "City St Georges University of London",
    "Coventry University",
    "Cumbria University",
    "De Montfort University",
    "University of Derby",
    "University of Dundee",
    "Durham University",
    "University of East Anglia",
    "University of East London",
    "Edge Hill University",
    "University of Edinburgh",
    "University of Essex",
    "University of Exeter",
    "University of Glamorgan",
    "University of Glasgow",
    "Glasgow Caledonian",
    "University of Gloucestershire",
    "Goldsmiths, University of London",
    "University of Greenwich",
    "Heriot Watt University",
    "University of Hertfordshire",
    "University of Huddersfield",
    "University of Hull",
    "Imperial College",
    "University of Keele",
    "University of Kent",
    "King’s College London",
    "Kingston University",
    "Lampeter, University of Wales",
    "Lancaster University",
    "University of Leeds",
    "Leeds Metropolitan University",
    "University of Leicester",
    "University of Lincoln",
    "University of Liverpool",
    "Liverpool Hope University",
    "Liverpool John Moores University",
    "London Metropolitan University",
    "London School of Economics and Political Science",
    "London South Bank University",
    "Loughborough University",
    "University of Manchester",
    "Manchester Metropolitan University",
    "Middlesex University",
    "Napier University",
    "Newcastle University",
    "University of Wales, Newport",
    "University of Northampton",
    "Northumbria University",
    "University of Nottingham",
    "Nottingham Trent University",
    "University of Oxford",
    "Oxford Brookes University",
    "University of Plymouth",
    "University of Portsmouth",
    "Queen Margaret University",
    "Queen Mary, University of London",
    "Queen’s University, Belfast",
    "University of Reading",
    "The Robert Gordon University",
    "Roehampton University",
    "Royal Holloway, University of London",
    "University of St Andrews",
    "University of Salford",
    "School of African and Oriental Studies, London",
    "University of Sheffield",
    "Sheffield Hallam University",
    "University of Southampton",
    "Southampton Solent",
    "Staffordshire University",
    "University of Stirling",
    "University of Strathclyde",
    "University of Sunderland",
    "University of Surrey",
    "University of Sussex",
    "Swansea University",
    "Swansea Metropolitan University",
    "University of Teesside",
    "Thames Valley University",
    "University of Ulster",
    "University of the Arts London",
    "University College London",
    "University of Warwick",
    "University of the West of England, Bristol",
    "University of the West of Scotland",
    "University of Westminster",
    "University of Winchester",
    "University of Wolverhampton",
    "University of Worcester",
    "University of York",
    "York St John University",

    "Other University",
    "Community Member",
    "Prefer not to say",
  ];

  const validateForm = () => {
    const newErrors: { name?: string; university?: string } = {};

    if (userInfo.saveToLeaderboard) {
      if (!userInfo.name.trim()) {
        newErrors.name = "Name is required to appear on leaderboard";
      } else if (userInfo.name.trim().length < 2) {
        newErrors.name = "Name must be at least 2 characters";
      }

      if (!userInfo.university.trim()) {
        newErrors.university = "University/affiliation is required";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(userInfo);
    }
  };

  const handleInputChange = (
    field: keyof UserInfo,
    value: string | boolean
  ) => {
    setUserInfo((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear errors when user starts typing
    if (errors[field as keyof typeof errors]) {
      setErrors((prev) => ({
        ...prev,
        [field]: undefined,
      }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 flex items-center justify-center p-4">
      <div className="bg-white shadow-xl rounded-2xl max-w-md w-full overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-6">
          <div className="text-center">
            <FaGlobeAmericas className="text-4xl mx-auto mb-3 opacity-90" />
            <h2 className="text-2xl font-bold mb-2">
              Join the EcoBee Community!
            </h2>
            <p className="text-green-100 text-sm">
              Help inspire others by sharing your sustainability journey
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          {/* Leaderboard Toggle */}
          <div className="mb-6">
            <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={userInfo.saveToLeaderboard}
                onChange={(e) =>
                  handleInputChange("saveToLeaderboard", e.target.checked)
                }
                className="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500"
              />
              <div>
                <span className="text-gray-800 font-medium">
                  Add me to the leaderboard
                </span>
                <p className="text-gray-600 text-sm">
                  Share your score to inspire others
                </p>
              </div>
            </label>
          </div>

          {userInfo.saveToLeaderboard && (
            <>
              {/* Name Input */}
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  <FaUser className="inline mr-2" />
                  Your Name or Pseudonym
                </label>
                <input
                  type="text"
                  value={userInfo.name}
                  onChange={(e) => handleInputChange("name", e.target.value)}
                  placeholder="Enter your name or a fun pseudonym"
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
                    errors.name
                      ? "border-red-300 focus:ring-red-500"
                      : "border-gray-300 focus:ring-green-500"
                  }`}
                  disabled={loading}
                />
                {errors.name && (
                  <p className="text-red-500 text-xs mt-1">{errors.name}</p>
                )}
              </div>

              {/* University Input */}
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2">
                  <FaUniversity className="inline mr-2" />
                  University or Affiliation
                </label>
                <select
                  value={userInfo.university}
                  onChange={(e) =>
                    handleInputChange("university", e.target.value)
                  }
                  className={`w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 transition-colors ${
                    errors.university
                      ? "border-red-300 focus:ring-red-500"
                      : "border-gray-300 focus:ring-green-500"
                  }`}
                  disabled={loading}
                  title="Select your university or affiliation"
                  aria-label="University or affiliation selection"
                >
                  <option value="">Select your affiliation</option>
                  {universityOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
                {errors.university && (
                  <p className="text-red-500 text-xs mt-1">
                    {errors.university}
                  </p>
                )}
              </div>
            </>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-3">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-green-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <FaCheck />
                  <span>
                    {userInfo.saveToLeaderboard
                      ? "Join Leaderboard"
                      : "Continue"}
                  </span>
                </>
              )}
            </button>

            <button
              type="button"
              onClick={onSkip}
              disabled={loading}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
            >
              <FaTimes />
              <span>Skip</span>
            </button>
          </div>

          {/* Privacy Note */}
          <div className="mt-4 text-center">
            <p className="text-gray-500 text-xs">
              🔒 Your information is used only for the leaderboard and community
              features
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
