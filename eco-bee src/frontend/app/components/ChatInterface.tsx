"use client";
import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  FaLeaf,
  FaGlobe,
  FaHeart,
  FaUsers,
  FaArrowRight,
  FaSpinner,
  FaTrophy,
  FaLightbulb,
  FaChartBar,
  FaRobot,
  FaComment,
  FaPlay,
  FaPause
} from "react-icons/fa";

interface Message {
  id: string;
  type: "bot" | "user" | "system";
  content: string;
  timestamp: Date;
  metadata?: any;
}

interface ChatInterfaceProps {
  onComplete?: (data: any) => void;
}

type ChatState = 
  | "welcome" 
  | "quiz_intro" 
  | "quiz_in_progress" 
  | "image_capture" 
  | "scoring" 
  | "results" 
  | "recommendations" 
  | "reflection" 
  | "leaderboard" 
  | "feedback"
  | "complete";

interface EcoBeeAvatar {
  expression: "happy" | "thinking" | "excited" | "neutral";
  isTyping: boolean;
}

export default function ChatInterface({ onComplete }: ChatInterfaceProps) {
  const router = useRouter();
  const [chatState, setChatState] = useState<ChatState>("welcome");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [avatar, setAvatar] = useState<EcoBeeAvatar>({ expression: "happy", isTyping: false });
  const [currentInput, setCurrentInput] = useState("");
  const [sessionData, setSessionData] = useState<any>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showOptions, setShowOptions] = useState<string[]>([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initialize chat with welcome message
    if (messages.length === 0) {
      addBotMessage(
        "🐝 Hi there! I'm EcoBee, your personal sustainability companion! I'm here to help you understand and reduce your environmental impact using the planetary boundaries framework.",
        { expression: "happy" }
      );
      
      setTimeout(() => {
        addBotMessage(
          "Ready to discover your EcoScore and get personalized recommendations? This will take about 5 minutes and could help make a real difference for our planet! 🌍",
          { expression: "excited", showOptions: ["Let's start!", "Tell me more first", "What's an EcoScore?"] }
        );
      }, 2000);
    }
  }, []);

  const addBotMessage = (content: string, metadata?: any) => {
    setIsTyping(true);
    setAvatar({ expression: metadata?.expression || "thinking", isTyping: true });
    
    setTimeout(() => {
      const message: Message = {
        id: Date.now().toString(),
        type: "bot",
        content,
        timestamp: new Date(),
        metadata
      };
      
      setMessages(prev => [...prev, message]);
      setIsTyping(false);
      setAvatar({ expression: metadata?.expression || "happy", isTyping: false });
      
      if (metadata?.showOptions) {
        setShowOptions(metadata.showOptions);
      }
    }, 1000 + Math.random() * 1500); // Simulate typing delay
  };

  const addUserMessage = (content: string, metadata?: any) => {
    const message: Message = {
      id: Date.now().toString(),
      type: "user",
      content,
      timestamp: new Date(),
      metadata
    };
    
    setMessages(prev => [...prev, message]);
    setShowOptions([]);
  };

  const addSystemMessage = (content: string, metadata?: any) => {
    const message: Message = {
      id: Date.now().toString(),
      type: "system",
      content,
      timestamp: new Date(),
      metadata
    };
    
    setMessages(prev => [...prev, message]);
  };

  const handleOptionClick = (option: string) => {
    addUserMessage(option);
    processUserInput(option);
  };

  const handleInputSubmit = () => {
    if (currentInput.trim()) {
      addUserMessage(currentInput);
      processUserInput(currentInput);
      setCurrentInput("");
    }
  };

  const processUserInput = (input: string) => {
    const inputLower = input.toLowerCase();
    
    switch (chatState) {
      case "welcome":
        if (inputLower.includes("start") || inputLower.includes("begin") || inputLower.includes("yes")) {
          handleStartQuiz();
        } else if (inputLower.includes("more") || inputLower.includes("tell")) {
          handleExplainMore();
        } else if (inputLower.includes("ecoscore") || inputLower.includes("what")) {
          handleExplainEcoScore();
        } else {
          addBotMessage(
            "I'm excited to help you! Would you like to start your sustainability assessment or learn more about how it works?",
            { showOptions: ["Start assessment", "How does it work?", "What data do you collect?"] }
          );
        }
        break;
        
      case "quiz_intro":
        handleQuizProgress(input);
        break;
        
      case "reflection":
        handleReflection(input);
        break;
        
      case "feedback":
        handleFeedback(input);
        break;
        
      default:
        addBotMessage("I'm processing your response... Let me think about that! 🤔");
    }
  };

  const handleStartQuiz = () => {
    setChatState("quiz_intro");
    addBotMessage(
      "Perfect! Let's dive in. I'll ask you about 5-7 quick questions covering your daily choices in food, clothing, transport, and lifestyle. Each answer helps me calculate your impact on Earth's planetary boundaries.",
      { expression: "excited" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "📝 **Question 1 of 7**: What best describes your main meal today?",
        { 
          expression: "neutral",
          showOptions: [
            "🥗 Plant-based (veggies, grains, legumes)",
            "🍖 Meat-heavy (beef, pork, lamb)",
            "🐟 Mixed with fish/chicken",
            "🥪 Processed/packaged meal",
            "☕ Just snacks or drinks"
          ]
        }
      );
    }, 2500);
  };

  const handleExplainMore = () => {
    addBotMessage(
      "Great question! I use the **Planetary Boundaries framework** - that's science-backed research from the Stockholm Resilience Centre about Earth's safe operating space.",
      { expression: "thinking" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "I look at 5 key boundaries: 🌡️ Climate Change, 🌱 Biodiversity, 💧 Water Use, 🌊 Chemical Pollution, and ⚡ Nutrient Cycles. Your choices affect all of these!",
        { 
          expression: "happy",
          showOptions: ["That sounds important!", "How do you calculate my impact?", "Ready to start!"]
        }
      );
    }, 3000);
  };

  const handleExplainEcoScore = () => {
    addBotMessage(
      "Your **EcoScore** is like a sustainability report card! It's a number from 0-100 that shows how your daily choices impact Earth's planetary boundaries.",
      { expression: "excited" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "🎯 Lower scores are better (less environmental pressure). I'll show you exactly where you stand and give you personalized actions to improve!",
        { 
          expression: "happy",
          showOptions: ["Cool, let's see my score!", "How accurate is this?", "What if my score is high?"]
        }
      );
    }, 2500);
  };

  const handleQuizProgress = (input: string) => {
    // This would integrate with the actual quiz component
    // For now, simulate quiz progression
    const currentQuestion = sessionData.currentQuestion || 1;
    
    // Store the answer
    setSessionData((prev: any) => ({
      ...prev,
      [`question_${currentQuestion}`]: input,
      currentQuestion: currentQuestion + 1
    }));

    if (currentQuestion < 7) {
      // Continue with next question
      const nextQuestion = currentQuestion + 1;
      const questions = [
        "🚗 How did you travel most today?",
        "👕 What's your clothing style like?", 
        "🏠 How would you describe your lifestyle?",
        "💼 What's your intended career path?",
        "♻️ How often do you recycle/reuse?",
        "🤔 One thing you'd like to improve about your environmental impact?"
      ];
      
      const options = [
        ["🚶 Walking", "🚲 Cycling", "🚌 Public transport", "🚗 Car", "✈️ Flew somewhere"],
        ["👗 Love fashion/shopping", "👖 Practical basics", "♻️ Second-hand/sustainable", "🛍️ Mix of everything"],
        ["🌱 Very eco-conscious", "📱 Average consumption", "🛒 I like nice things", "🤷 Haven't thought about it"],
        ["💻 Tech/Software", "🏥 Healthcare", "🎓 Education", "🏭 Business/Finance", "🔬 Science/Research", "🎨 Creative/Arts"],
        ["♻️ Always", "🔄 Often", "🤷 Sometimes", "😅 Rarely"],
        ["🍃 Eating habits", "🚗 Transportation", "👕 Shopping choices", "⚡ Energy use", "💭 Just general awareness"]
      ];
      
      setTimeout(() => {
        addBotMessage(
          `**Question ${nextQuestion} of 7**: ${questions[nextQuestion - 2]}`,
          { 
            expression: "neutral",
            showOptions: options[nextQuestion - 2]
          }
        );
      }, 1500);
    } else {
      // Quiz complete, move to scoring
      handleQuizComplete();
    }
  };

  const handleQuizComplete = () => {
    setChatState("scoring");
    addBotMessage(
      "Excellent! 🎉 I've got all your responses. Let me crunch the numbers and calculate your EcoScore across all planetary boundaries...",
      { expression: "thinking" }
    );
    
    // Simulate scoring process
    setTimeout(() => {
      addSystemMessage("🔄 Analyzing your food choices...");
    }, 1000);
    
    setTimeout(() => {
      addSystemMessage("🔄 Calculating transport impact...");
    }, 2000);
    
    setTimeout(() => {
      addSystemMessage("🔄 Processing lifestyle factors...");
    }, 3000);
    
    setTimeout(() => {
      addSystemMessage("🔄 Generating your planetary boundary profile...");
    }, 4000);
    
    setTimeout(() => {
      handleShowResults();
    }, 5500);
  };

  const handleShowResults = () => {
    setChatState("results");
    
    // Simulate realistic EcoScore (this would come from the backend)
    const mockEcoScore = {
      composite: 58,
      grade: "C+",
      boundaries: {
        climate: 62,
        biosphere: 45,
        biogeochemical: 55,
        freshwater: 68,
        aerosols: 52
      }
    };
    
    setSessionData((prev: any) => ({ ...prev, ecoScore: mockEcoScore }));
    
    addBotMessage(
      `🎯 **Your EcoScore: ${mockEcoScore.composite}/100 (Grade: ${mockEcoScore.grade})**\n\nThis means you're putting moderate pressure on Earth's systems. There's definitely room for improvement, but you're not in the red zone!`,
      { expression: "neutral" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "📊 **Your Boundary Breakdown:**\n🌡️ Climate: " + mockEcoScore.boundaries.climate + "/100\n🌱 Biodiversity: " + mockEcoScore.boundaries.biosphere + "/100\n💧 Water: " + mockEcoScore.boundaries.freshwater + "/100\n⚡ Nutrients: " + mockEcoScore.boundaries.biogeochemical + "/100\n🌊 Pollution: " + mockEcoScore.boundaries.aerosols + "/100",
        { expression: "happy" }
      );
    }, 3000);
    
    setTimeout(() => {
      addBotMessage(
        "Want to see how you compare with other students and get personalized recommendations?",
        { 
          expression: "excited",
          showOptions: ["Show me the leaderboard! 🏆", "Give me recommendations! 💡", "How can I improve?"]
        }
      );
    }, 5000);
  };

  const handleReflection = (input: string) => {
    setChatState("feedback");
    setSessionData((prev: any) => ({ ...prev, reflection: input }));
    
    addBotMessage(
      "That's a great choice! 🌟 Every small action adds up to make a real difference.",
      { expression: "happy" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "One last question: How useful was this EcoScore experience for you?",
        { 
          expression: "neutral",
          showOptions: [
            "⭐ Very useful - I learned a lot!",
            "👍 Somewhat useful",
            "🤷 Not sure it will change anything",
            "💡 Useful but need more specific advice"
          ]
        }
      );
    }, 2000);
  };

  const handleFeedback = (input: string) => {
    setChatState("complete");
    setSessionData((prev: any) => ({ ...prev, feedback: input }));
    
    addBotMessage(
      "Thank you so much! 🙏 Your feedback helps me become a better sustainability companion.",
      { expression: "happy" }
    );
    
    setTimeout(() => {
      addBotMessage(
        "🎉 **You're all set!** Remember: sustainable living is a journey, not a destination. Small consistent actions create big impacts over time.",
        { 
          expression: "excited",
          showOptions: ["Restart with new answers", "Share my results", "Learn more about planetary boundaries"]
        }
      );
    }, 2500);
    
    if (onComplete) {
      setTimeout(() => {
        onComplete(sessionData);
      }, 4000);
    }
  };

  const getAvatarEmoji = () => {
    if (avatar.isTyping) return "🤔";
    
    switch (avatar.expression) {
      case "happy": return "😊";
      case "thinking": return "🤔";
      case "excited": return "🤩";
      default: return "🐝";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-blue-50 to-yellow-50 flex flex-col">
      {/* Header with EcoBee branding */}
      <div className="bg-white shadow-sm border-b border-green-200 p-4">
        <div className="max-w-4xl mx-auto flex items-center gap-3">
          <div className="text-2xl">🐝</div>
          <div>
            <h1 className="text-xl font-bold text-green-800">EcoBee</h1>
            <p className="text-sm text-green-600">Your Personal Sustainability Companion</p>
          </div>
          <div className="ml-auto text-sm text-gray-500">
            {chatState === "welcome" && "Ready to start"}
            {chatState === "quiz_intro" && "Assessment in progress"}
            {chatState === "quiz_in_progress" && "Answering questions"}
            {chatState === "scoring" && "Calculating EcoScore"}
            {chatState === "results" && "Results ready"}
            {chatState === "complete" && "Session complete"}
          </div>
        </div>
      </div>

      {/* Chat messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.type === "user" ? "flex-row-reverse" : ""}`}
            >
              {/* Avatar */}
              {message.type === "bot" && (
                <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-lg">
                  {getAvatarEmoji()}
                </div>
              )}
              
              {message.type === "user" && (
                <div className="flex-shrink-0 w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-lg">
                  👤
                </div>
              )}

              {/* Message content */}
              <div
                className={`max-w-2xl p-3 rounded-lg ${
                  message.type === "bot"
                    ? "bg-white border border-green-200 text-gray-800"
                    : message.type === "user"
                    ? "bg-blue-500 text-white"
                    : "bg-gray-100 text-gray-600 text-sm"
                }`}
              >
                <div className="whitespace-pre-wrap">{message.content}</div>
                
                {/* Show timestamp for completed messages */}
                <div className={`text-xs mt-1 opacity-60 ${
                  message.type === "user" ? "text-blue-100" : "text-gray-500"
                }`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </div>
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center text-lg">
                🤔
              </div>
              <div className="max-w-2xl p-3 rounded-lg bg-white border border-green-200">
                <div className="flex items-center gap-1">
                  <FaSpinner className="animate-spin text-green-600" />
                  <span className="text-gray-600">EcoBee is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-green-200 p-4">
        <div className="max-w-4xl mx-auto">
          {/* Quick options */}
          {showOptions.length > 0 && (
            <div className="mb-4 flex flex-wrap gap-2">
              {showOptions.map((option, index) => (
                <button
                  key={index}
                  onClick={() => handleOptionClick(option)}
                  className="px-4 py-2 bg-green-100 hover:bg-green-200 text-green-800 rounded-full text-sm transition-colors"
                >
                  {option}
                </button>
              ))}
            </div>
          )}

          {/* Text input */}
          <div className="flex gap-3">
            <input
              type="text"
              value={currentInput}
              onChange={(e) => setCurrentInput(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleInputSubmit()}
              placeholder="Type your response here..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              disabled={isTyping || showOptions.length > 0}
            />
            <button
              onClick={handleInputSubmit}
              disabled={!currentInput.trim() || isTyping || showOptions.length > 0}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-300 text-white rounded-lg flex items-center gap-2 transition-colors"
            >
              <FaArrowRight />
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
