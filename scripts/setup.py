"""Setup script for Knowledge Engineering Platform"""
import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import init_db
from backend.app.services.connectors import connector_manager
from backend.app.services.metadata import metadata_engine
from backend.app.services.evaluation import evaluation_engine


async def setup_database():
    """Initialize database tables"""
    print("Initializing database...")
    await init_db()
    print("Database initialized successfully")


async def setup_directories():
    """Create necessary directories"""
    dirs = [
        "data",
        "data/uploads",
        "data/exports",
        "models",
        "evaluation/datasets",
        "evaluation/reports",
        "logs"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    print("Directories created successfully")


async def setup_sample_data():
    """Setup sample data for testing"""
    print("Setting up sample data...")
    
    # Register sample evaluation dataset
    sample_questions = [
        {
            "question": "What is a primary key in databases?",
            "expected_source": "database-basics.pdf",
            "expected_answer": "A primary key is a unique identifier for each row in a database table"
        },
        {
            "question": "What is SQL SELECT used for?",
            "expected_source": "sql-basics.pdf",
            "expected_answer": "SQL SELECT is used to retrieve data from a database"
        }
    ]
    
    evaluation_engine.register_dataset("sample_dataset", sample_questions)
    print("Sample data created successfully")


async def main():
    """Main setup function"""
    print("=" * 60)
    print("Knowledge Engineering Platform - Setup")
    print("=" * 60)
    
    await setup_directories()
    await setup_database()
    await setup_sample_data()
    
    print("=" * 60)
    print("Setup completed successfully!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start the backend: uvicorn backend.main:app --reload")
    print("2. Start the worker: python workers/worker.py")
    print("3. Start the frontend: cd frontend && npm run dev")
    print("4. Visit http://localhost:8000/docs for API documentation")


if __name__ == "__main__":
    asyncio.run(main())