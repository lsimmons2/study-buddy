FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8000
# EXPOSE 8000

# Run the FastAPI app with Uvicorn
# CMD ["uvicorn", "app:app", "--no-use-colors", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "run.py"]
