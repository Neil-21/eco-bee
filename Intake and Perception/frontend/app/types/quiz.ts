import { ReactNode } from "react";

export interface QuizQuestion {
  id: string;
  text: string;
  type: "single" | "multiple" | "scale" | "text" | "image";
  category: "food" | "clothing" | "transport" | "lifestyle" | "reflection";
  options?: Array<{
    value: string;
    label: string;
    icon?: ReactNode;
    description?: string;
  }>;
  required: boolean;
  scaleMin?: number;
  scaleMax?: number;
  scaleLabels?: [string, string];
  placeholder?: string;
  validation?: (value: any) => string | null;
}

export interface QuizResponse {
  question_id: string;
  question_text: string;
  answer: string | string[];
  category: string;
}

export interface QuizState {
  currentQuestionIndex: number;
  responses: QuizResponse[];
  isComplete: boolean;
  capturedItems: Array<{
    type: string;
    category: string;
    materials: string[];
    barcode?: string;
    confidence: number;
    source: string;
  }>;
}

// Comprehensive quiz questions covering all planetary boundaries
export const QUIZ_QUESTIONS: QuizQuestion[] = [
  {
    id: "food_today",
    text: "What best describes your main meal today?",
    type: "single",
    category: "food",
    required: true,
    options: [
      {
        value: "plant-based",
        label: "Plant-based",
        description: "Vegetables, fruits, grains, legumes",
      },
      {
        value: "mixed",
        label: "Mixed (plant & animal)",
        description: "Balanced combination of plant and animal products",
      },
      {
        value: "meat-heavy",
        label: "Meat-heavy",
        description: "Primarily meat, fish, or animal products",
      },
      {
        value: "packaged",
        label: "Processed/Packaged",
        description: "Pre-made meals, snacks, convenience foods",
      },
    ],
  },
  {
    id: "food_origin",
    text: "Where did your food come from?",
    type: "single",
    category: "food",
    required: true,
    options: [
      {
        value: "local",
        label: "Local/farmers market",
        description: "Within 50km radius",
      },
      {
        value: "supermarket",
        label: "Supermarket",
        description: "Regular grocery store",
      },
      {
        value: "restaurant",
        label: "Restaurant/takeaway",
        description: "Prepared food service",
      },
      {
        value: "homegrown",
        label: "Home-grown",
        description: "Grown yourself or by family",
      },
      {
        value: "unknown",
        label: "Don't know",
        description: "Origin uncertain",
      },
    ],
  },
  {
    id: "clothing_today",
    text: "What materials make up most of your outfit today?",
    type: "single",
    category: "clothing",
    required: true,
    options: [
      {
        value: "cotton",
        label: "Cotton",
        description: "Natural cotton fabrics",
      },
      {
        value: "synthetic",
        label: "Synthetic",
        description: "Polyester, nylon, acrylic",
      },
      { value: "wool", label: "Wool", description: "Natural wool materials" },
      {
        value: "mixed",
        label: "Mixed materials",
        description: "Combination of different fabrics",
      },
      {
        value: "recycled",
        label: "Recycled/second-hand",
        description: "Previously owned or recycled materials",
      },
    ],
  },
  {
    id: "transport_today",
    text: "How did you get here today?",
    type: "single",
    category: "transport",
    required: true,
    options: [
      { value: "walk", label: "Walking", description: "On foot" },
      {
        value: "bike",
        label: "Bicycle",
        description: "Personal or shared bike",
      },
      {
        value: "public",
        label: "Public transport",
        description: "Bus, train, tram",
      },
      { value: "car", label: "Car", description: "Personal or shared car" },
      {
        value: "electric",
        label: "Electric vehicle",
        description: "Electric car or scooter",
      },
      {
        value: "other",
        label: "Other",
        description: "Different transport method",
      },
    ],
  },
  {
    id: "distance_traveled",
    text: "Approximately how far did you travel today (total)?",
    type: "single",
    category: "transport",
    required: true,
    options: [
      { value: "under_5km", label: "Under 5km", description: "Local travel" },
      { value: "5_20km", label: "5-20km", description: "Medium distance" },
      { value: "20_50km", label: "20-50km", description: "Longer commute" },
      {
        value: "over_50km",
        label: "Over 50km",
        description: "Long distance travel",
      },
    ],
  },
  {
    id: "water_usage",
    text: "How would you rate your water consciousness today?",
    type: "scale",
    category: "lifestyle",
    required: true,
    scaleMin: 1,
    scaleMax: 5,
    scaleLabels: ["Used freely", "Very conscious"],
  },
  {
    id: "waste_reduction",
    text: "Which waste reduction actions did you take today?",
    type: "multiple",
    category: "lifestyle",
    required: false,
    options: [
      { value: "reusable_bottle", label: "Used reusable water bottle" },
      { value: "reusable_bag", label: "Used reusable shopping bag" },
      { value: "avoided_plastic", label: "Avoided single-use plastics" },
      { value: "composted", label: "Composted organic waste" },
      { value: "recycled", label: "Recycled materials properly" },
      { value: "repaired", label: "Repaired instead of replacing" },
      { value: "none", label: "None of these" },
    ],
  },
  {
    id: "reflection",
    text: "What's one thing you could change to reduce your environmental impact?",
    type: "text",
    category: "reflection",
    required: false,
    placeholder:
      "Share your thoughts on how you could make a positive change...",
  },
];

export const getQuestionsByCategory = (category: string): QuizQuestion[] => {
  return QUIZ_QUESTIONS.filter((q) => q.category === category);
};

export const validateQuizResponse = (
  question: QuizQuestion,
  answer: any
): string | null => {
  if (
    question.required &&
    (!answer || (Array.isArray(answer) && answer.length === 0))
  ) {
    return "This question is required";
  }

  if (question.validation) {
    return question.validation(answer);
  }

  return null;
};

export const calculateQuizProgress = (responses: QuizResponse[]): number => {
  const requiredQuestions = QUIZ_QUESTIONS.filter((q) => q.required).length;
  const answeredRequired = responses.filter((r) => {
    const question = QUIZ_QUESTIONS.find((q) => q.id === r.question_id);
    return question?.required && r.answer;
  }).length;

  return Math.round((answeredRequired / requiredQuestions) * 100);
};

export const createQuizResponse = (
  question: QuizQuestion,
  answer: any
): QuizResponse => {
  return {
    question_id: question.id,
    question_text: question.text,
    answer: answer,
    category: question.category,
  };
};
