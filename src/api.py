# ecoscore/api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .intake import router as intake_router

app = FastAPI()

# Optional: Add CORS middleware if your frontend and backend are on different domains
# This is an alternative to the Next.js proxy rewrite for production
# origins = [
#     "http://localhost:3000", # Your Next.js app
#     # Add your production frontend URL here
# ]
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Include the router from intake.py
app.include_router(intake_router)

@app.get("/")
def read_root():
    return {"message": "EcoScore API is running"}