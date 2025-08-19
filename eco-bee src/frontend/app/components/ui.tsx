"use client";
import React from "react";

// Bee component with glowing antennae
export function Bee({ size = 140 }: { size?: number }) {
  return (
    <div className="relative inline-block">
      <div
        className="rounded-[28%] bg-gradient-to-br from-yellow-400 to-yellow-600 overflow-hidden"
        style={{
          width: size,
          height: size,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: "8px",
        }}
      >
        <img
          src="/THE eco-bee.png"
          alt="EcoBee"
          style={{
            maxWidth: "100%",
            maxHeight: "100%",
            objectFit: "contain",
          }}
          onError={(e) => {
            console.log("Image failed to load, showing fallback");
            e.currentTarget.style.display = "none";
            const fallback = document.createElement("div");
            fallback.innerHTML = "🐝";
            fallback.style.fontSize = "48px";
            e.currentTarget.parentElement?.appendChild(fallback);
          }}
          onLoad={() => console.log("Image loaded successfully")}
        />
      </div>
      {/* Antennae glow */}
      <span className="pointer-events-none absolute -top-2 left-1/3 h-5 w-5 rounded-full bg-yellow-400/70 blur-[6px]" />
      <span className="pointer-events-none absolute -top-2 right-1/3 h-5 w-5 rounded-full bg-yellow-400/70 blur-[6px]" />
    </div>
  );
}

// Glass card component
export function Card({
  className = "",
  children,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={`glass ${className}`} {...props}>
      {children}
    </div>
  );
}

// Enhanced button component
export function Button({
  children,
  className = "",
  variant = "default",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "default" | "primary" | "ghost";
}) {
  const baseClass = "btn";
  const variantClass =
    variant === "primary"
      ? "btn-primary"
      : variant === "ghost"
      ? "btn-ghost"
      : "";

  return (
    <button className={`${baseClass} ${variantClass} ${className}`} {...props}>
      {children}
    </button>
  );
}

// Section title component
export function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-lg font-semibold tracking-tight text-neutral-200 mb-4">
      {children}
    </h2>
  );
}

// Feature card component for dashboard
export function FeatureCard({
  icon,
  title,
  description,
  onClick,
  className = "",
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick?: () => void;
  className?: string;
}) {
  return (
    <div className={`feature-card ${className}`} onClick={onClick}>
      <div className="feature-icon">{icon}</div>
      <div className="feature-title">{title}</div>
      <div className="feature-description">{description}</div>
    </div>
  );
}

// Progress bar component
export function ProgressBar({
  progress,
  className = "",
}: {
  progress: number;
  className?: string;
}) {
  return (
    <div className={`quiz-progress ${className}`}>
      <div
        className="quiz-progress-bar"
        style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
      />
    </div>
  );
}

// Loading spinner
export function Spinner({
  size = 24,
  className = "",
}: {
  size?: number;
  className?: string;
}) {
  return (
    <div
      className={`spinner ${className}`}
      style={{ width: size, height: size }}
    />
  );
}

// Brand header component
export function BrandHeader() {
  return (
    <header className="brand container" role="banner">
      <div className="brand-badge">
        <span className="badge-dot" />
        <span>EcoBee</span>
      </div>
      <nav className="caption" aria-label="Tagline">
        AI-powered sustainability coach
      </nav>
    </header>
  );
}

// Chat message component
export function ChatMessage({
  type,
  content,
  avatar,
}: {
  type: "user" | "bot" | "system";
  content: string;
  avatar?: string;
}) {
  return (
    <div className={`chat-message ${type}`}>
      <div className="chat-avatar">
        {type === "bot" ? "🐝" : type === "user" ? "👤" : "💡"}
      </div>
      <div className="chat-content">{content}</div>
    </div>
  );
}

// Chat input component
export function ChatInput({
  onSend,
  disabled = false,
  placeholder = "Type your message...",
}: {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}) {
  const [message, setMessage] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSend(message.trim());
      setMessage("");
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      <input
        className="chat-input"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
      />
      <Button
        type="submit"
        variant="primary"
        disabled={!message.trim() || disabled}
      >
        Send
      </Button>
    </form>
  );
}
