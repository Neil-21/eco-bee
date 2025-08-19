# 🐝 Eco-Bee: Smarter Sustainability & Environmental Intelligence

Welcome to **Eco-Bee**, an open-source platform for tracking, scoring, and improving sustainable actions—powered by AI, planetary boundaries science, and seamless product intelligence. Eco-Bee helps individuals and communities make smarter, greener choices through data-driven insights and practical recommendations.

---

## 🚀 What is Eco-Bee?

Eco-Bee is a cross-platform solution offering:

- **EcoScore Calculation:** Quantifies your ecological impact across key planetary boundaries (climate, biodiversity, water, land, pollution, and more).
- **Vision AI & Barcode Scanning:** Instantly classify products and meals using images or barcodes, leveraging state-of-the-art models (Pixtral, Node2Vec, and more).
- **Recommendation Engine:** Receive customized sustainability actions to reduce your footprint, powered by graph embeddings and real-world feasibility.
- **Leaderboards & Social Features:** Track scores, share progress, and compete for a greener planet.
- **Campus/Local Resources:** Tap into actionable sustainability resources and events in your community.

---

## 🧩 Repo Structure

| Directory/File        | Description                                      |
|----------------------|--------------------------------------------------|
| `eco-bee src/backend/` | **Python FastAPI backend**: scoring, intake, recommendations, AI integration |
| `ecoscore.py`        | EcoScore calculation & normalization logic       |
| `generate_embedding.py` | Node2Vec graph embeddings for recommendations   |
| `server.ts` & `recommend.ts` | **TypeScript/Node.js API**: leaderboards, scores, and action recommendations |
| `embeddings.json`    | Precomputed action embeddings for Node2Vec       |
| `lookup.json`        | Impact factor data for EcoScore                  |

---

## ⚡️ Features

- **Multi-modal intake:** Supports quizzes, images, barcode scans, and direct product inputs.
- **Planetary Boundaries Model:** Scientifically grounded scoring for climate, biodiversity, water, land, pollution, and more.
- **Pixtral Vision AI Integration:** Fast, accurate product and meal classification from images.
- **Node2Vec-based Recommendations:** Smart, personalized action suggestions using graph embeddings.
- **REST APIs:** Easy integration for web/mobile apps.
- **Campus/Community Resources:** Localized sustainability tips and opportunities.

---

## 💻 Getting Started

### Backend (Python/FastAPI)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Run the FastAPI backend
uvicorn eco-bee\ src/backend/app:app --reload
```

### Node.js API (TypeScript/Express)

```bash
# Install Node.js dependencies
npm install

# Run the server
npx ts-node server.ts
```

### Embedding Generation

```bash
python generate_embedding.py
```

---

## 📦 Requirements

See [`requirements.txt`](./requirements.txt) for all Python and Node.js dependencies.

---

## 🌍 API Endpoints

- `/api/intake` – Intake and scoring
- `/api/classify-image` – Vision AI product/meal classification
- `/api/score` – EcoScore calculation
- `/api/leaderboard` – Leaderboard and score submissions
- `/api/recommend` – Sustainability action recommendations
- `/api/barcode-lookup` – Product info via barcode

More endpoints and details in the source code.


---

## 📚 References & Credits

- [Planetary Boundaries Framework](https://www.stockholmresilience.org/research/planetary-boundaries.html)
- [Pixtral Vision AI](https://huggingface.co/mistralai/Pixtral-8B-v0.1)
- [Node2Vec Graph Embedding](https://snap.stanford.edu/node2vec/)
- Data sources: OpenLCA, EcoInvent, campus sustainability programs

---

## 📝 License

MIT License. See [LICENSE](./LICENSE).

---

## 🐝 Let's build a smarter, greener future—one action at a time!
