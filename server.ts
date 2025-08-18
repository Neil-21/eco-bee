// server.ts
import express from "express";
import bodyParser from "body-parser";
import { getLeaderboard, submitScore, recommendActionsTopN } from "./recommend";

const app = express();
const PORT = 3000;

app.use(bodyParser.json());

// GET leaderboard
app.get("/api/leaderboard", (req, res) => {
  res.json(getLeaderboard());
});

// POST submit score
app.post("/api/submit-score", (req, res) => {
  const { name, score } = req.body;
  if (!name || typeof score !== "number") return res.status(400).json({ error: "Invalid payload" });
  const entry = submitScore(name, score);
  res.json(entry);
});

// GET recommended actions (optional seedId param)
app.get("/api/recommend", (req, res) => {
  const { seedId } = req.query;
  const recommendations = recommendActionsTopN(typeof seedId === "string" ? seedId : undefined);
  res.json(recommendations);
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
