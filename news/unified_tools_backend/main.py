# News AI Backend + RL Automation - Sprint Complete
# Main entry point for the FastAPI application

from app.api.main import app

# The complete application is now defined in app/api/main.py
# This file serves as the entry point for running the server

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting News AI Backend + RL Automation Sprint")
    print("✅ All 5 days completed - Production Ready")
    print("🌐 Server will be available at http://localhost:8000")
    print("📊 WebSocket server at ws://localhost:8765")
    uvicorn.run(app, host="0.0.0.0", port=8000)
