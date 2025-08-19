"use client";
import React, { useState, useRef, useEffect } from "react";
import { FaPaperPlane, FaRobot, FaUser, FaLeaf } from "react-icons/fa";
import { Bee, Card } from "./ui";

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatbotInterfaceProps {
  onClose?: () => void;
}

export default function ChatbotInterface({ onClose }: ChatbotInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      text: "Hi! I'm EcoBee, your sustainability assistant! 🌱 I can help you with eco-friendly tips, product recommendations, and answer questions about sustainable living. How can I help you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  
  const [inputText, setInputText] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: text.trim(),
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    setIsTyping(true);

    // Simulate bot response (in a real app, this would call your chatbot API)
    setTimeout(() => {
      const botResponse = generateBotResponse(text.trim());
      const botMessage: Message = {
        id: `bot-${Date.now()}`,
        text: botResponse,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000);
  };

  const generateBotResponse = (userInput: string): string => {
    const input = userInput.toLowerCase();
    
    if (input.includes("sustainable") || input.includes("eco")) {
      return "Great question about sustainability! 🌍 Here are some key tips: Choose products with minimal packaging, buy local when possible, and look for certifications like Fair Trade or organic labels. Would you like specific advice for any category?";
    }
    
    if (input.includes("plastic") || input.includes("waste")) {
      return "Reducing plastic waste is crucial! 🗂️ Try these steps: Use reusable bags and water bottles, choose glass or metal containers when possible, and recycle properly. Many products now come in biodegradable packaging too!";
    }
    
    if (input.includes("food") || input.includes("eat")) {
      return "Sustainable eating makes a big difference! 🥗 Consider: eating more plant-based meals, choosing local and seasonal produce, reducing food waste by planning meals, and supporting regenerative agriculture when possible.";
    }
    
    if (input.includes("clothing") || input.includes("fashion")) {
      return "Fashion can be sustainable too! 👕 Look for: quality pieces that last longer, second-hand or vintage items, brands using organic or recycled materials, and clothes made locally to reduce transport emissions.";
    }
    
    if (input.includes("energy") || input.includes("power")) {
      return "Energy efficiency is key! ⚡ Try: LED bulbs, unplugging devices when not in use, using energy-efficient appliances, and considering renewable energy options like solar panels if possible.";
    }
    
    if (input.includes("transport") || input.includes("travel")) {
      return "Sustainable transport helps the planet! 🚲 Options include: walking or cycling for short trips, using public transport, carpooling, choosing hybrid/electric vehicles, and offsetting emissions for necessary flights.";
    }
    
    if (input.includes("help") || input.includes("tips")) {
      return "I'm here to help with all your sustainability questions! 🌱 I can provide advice on: eco-friendly products, sustainable living tips, reducing your carbon footprint, and making environmentally conscious choices. What specific area interests you?";
    }
    
    // Default responses
    const defaultResponses = [
      "That's an interesting question! 🤔 While I focus on sustainability topics, I'd recommend checking our quiz for personalized eco-tips, or ask me about specific sustainable practices you'd like to learn about.",
      "I love helping with sustainability questions! 🌿 Could you tell me more about what specific environmental topic you're interested in? I can provide tips on food, fashion, energy, transport, and more!",
      "Thanks for chatting with me! 🐝 I'm specialized in sustainability and eco-friendly living. Feel free to ask about reducing waste, sustainable products, or green lifestyle choices!",
    ];
    
    return defaultResponses[Math.floor(Math.random() * defaultResponses.length)];
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputText);
    }
  };

  return (
    <Card className="max-w-md mx-auto h-[600px] flex flex-col">
      {/* Header */}
      <div className="glass-header p-4 border-b border-white/10 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Bee size={24} />
          <div>
            <h3 className="font-semibold text-white">EcoBee Assistant</h3>
            <p className="text-xs text-white/60">Sustainability Expert</p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="text-white/60 hover:text-white transition-colors"
          >
            ✕
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] flex items-start space-x-2 ${
                message.isUser ? "flex-row-reverse space-x-reverse" : ""
              }`}
            >
              {/* Avatar */}
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${
                  message.isUser
                    ? "bg-gradient-to-r from-blue-400 to-purple-400"
                    : "bg-gradient-to-r from-green-400 to-teal-400"
                }`}
              >
                {message.isUser ? <FaUser /> : <FaLeaf />}
              </div>

              {/* Message bubble */}
              <div
                className={`px-4 py-2 rounded-lg ${
                  message.isUser
                    ? "bg-gradient-to-r from-blue-500/20 to-purple-500/20 border border-blue-400/30 text-white"
                    : "glass-card-inner border border-green-400/30 text-white"
                }`}
              >
                <p className="text-sm">{message.text}</p>
                <p className="text-xs text-white/50 mt-1">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </p>
              </div>
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start">
            <div className="flex items-start space-x-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-400 to-teal-400 flex items-center justify-center text-sm">
                <FaLeaf />
              </div>
              <div className="glass-card-inner border border-green-400/30 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-2">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask me about sustainability..."
            className="flex-1 px-4 py-2 glass-input border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:border-green-400/50 transition-colors"
          />
          <button
            onClick={() => handleSendMessage(inputText)}
            disabled={!inputText.trim() || isTyping}
            className="px-4 py-2 bg-gradient-to-r from-green-400 to-teal-400 text-white rounded-lg hover:from-green-500 hover:to-teal-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center space-x-1"
          >
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </Card>
  );
}
