# Start local backend for development without redis+worker
cd backend/
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 55955