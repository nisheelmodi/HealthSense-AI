FROM python:3.9-slim

WORKDIR /app

# Copy requirements
COPY backend/requirements.txt ./backend/

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the backend code and ML models
COPY backend/ ./backend/
COPY ml/models/ ./ml/models/

# The application port is provided by the environment (e.g., PORT variable on Render)
# Run the FastAPI app
CMD ["python", "-m", "backend.main"]
