from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/run")
async def run(payload: dict):
    """Analyze finances"""
    try:
        from agents.simple_crew import analyze_finances
        
        financial_data = payload.get('financial_data', {})
        expenses = financial_data.get('expenses', [])
        
        print(f"DEBUG: Received {len(expenses)} expenses")
        
        result = analyze_finances(expenses)
        
        print(f"DEBUG: Result status: {result.get('status')}")
        print(f"DEBUG: Has analysis: {'analysis' in result}")
        print(f"DEBUG: Has recommendations: {'recommendations' in result}")
        print(f"DEBUG: Has budget: {'budget' in result}")
        
        # Return the result directly - it already has the right fields
        return result
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "analysis": "Error",
            "recommendations": "Error",
            "budget": "Error"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting API server on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)