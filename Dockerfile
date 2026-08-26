FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt ./backend/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend code and ML models
COPY backend/ ./backend/
COPY ml/models/ ./ml/models/

# Hugging Face Spaces exposes port 7860
EXPOSE 7860

# Run the FastAPI app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
