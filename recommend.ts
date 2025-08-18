// recommend.ts
import { v4 as uuidv4 } from "uuid";
import fs from "fs";
import path from "path";

// ----------------- Seed Dataset -----------------
export interface Action {
  id: string;
  name: string;
  domain: string;
  feasibility: number;
  boundary_gap: number;
}

export const actions: Action[] = [
  { id: "a1", name: "Campus Swap Event", domain: "swap", feasibility: 0.9, boundary_gap: 0.7 },
  { id: "a2", name: "Repair Café", domain: "repair", feasibility: 0.8, boundary_gap: 0.8 },
  { id: "a3", name: "Veggie Meal Option", domain: "veggie", feasibility: 0.6, boundary_gap: 0.9 },
  { id: "a4", name: "Bike Share", domain: "transport", feasibility: 0.7, boundary_gap: 0.6 },
];

// ----------------- Graph -----------------
export interface GraphNode {
  action: Action;
  neighbors: GraphNode[];
}

export const graph: { [id: string]: GraphNode } = {};
actions.forEach((a) => (graph[a.id] = { action: a, neighbors: [] }));
actions.forEach((a) => {
  actions.forEach((b) => {
    if (a.id !== b.id && a.domain === b.domain) {
      graph[a.id].neighbors.push(graph[b.id]);
    }
  });
});

// ----------------- Node2Vec Embeddings -----------------
interface Embeddings {
  [id: string]: number[];
}

const embeddingsPath = path.join(__dirname, "embeddings.json");
const embeddings: Embeddings = JSON.parse(fs.readFileSync(embeddingsPath, "utf-8"));

// Cosine similarity helper
function cosineSimilarity(vecA: number[], vecB: number[]): number {
  const dot = vecA.reduce((sum, val, i) => sum + val * vecB[i], 0);
  const magA = Math.sqrt(vecA.reduce((sum, val) => sum + val * val, 0));
  const magB = Math.sqrt(vecB.reduce((sum, val) => sum + val * val, 0));
  return dot / (magA * magB);
}

// Recommend top N based on similarity to a "seed" vector (optional)
export function recommendActionsTopN(seedId?: string, N = 4): Action[] {
  if (!seedId || !embeddings[seedId]) {
    // fallback: return top action per domain
    return Object.values(rankTopActionPerDomain());
  }

  const seedVector = embeddings[seedId];
  const scored = actions.map((a) => ({
    action: a,
    score: cosineSimilarity(seedVector, embeddings[a.id]),
  }));

  scored.sort((a, b) => b.score - a.score);
  return scored.slice(0, N).map((s) => s.action);
}

// ----------------- Rank Top Action per Domain -----------------
export function rankTopActionPerDomain(): { [domain: string]: Action } {
  const result: { [domain: string]: Action } = {};
  const grouped: { [domain: string]: Action[] } = {};
  actions.forEach((a) => {
    if (!grouped[a.domain]) grouped[a.domain] = [];
    grouped[a.domain].push(a);
  });
  for (const domain in grouped) {
    let top = grouped[domain][0];
    grouped[domain].forEach((a) => {
      const scoreA = a.feasibility * a.boundary_gap;
      const scoreTop = top.feasibility * top.boundary_gap;
      if (scoreA > scoreTop) top = a;
    });
    result[domain] = top;
  }
  return result;
}

// ----------------- Leaderboard -----------------
export interface ScoreEntry {
  id: string;
  name: string;
  score: number;
}

export const leaderboard: ScoreEntry[] = [];

export function submitScore(name: string, score: number) {
  const id = uuidv4();
  leaderboard.push({ id, name, score });
  return { id, name, score };
}

export function getLeaderboard(): ScoreEntry[] {
  return leaderboard.sort((a, b) => b.score - a.score);
}
