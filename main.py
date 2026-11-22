from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import farmer_routes, bank_routes

app = FastAPI(title="Agri Policy & Loan Transparency API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(farmer_routes.router, prefix="/api/farmer", tags=["Farmer View"])
app.include_router(bank_routes.router, prefix="/api/bank", tags=["Bank View"])

@app.get("/")
def root():
    return {"message": "Backend running cleanly"}
