FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m nltk.downloader punkt
RUN python -m nltk.downloader punkt_tab

# Copy application code
COPY . .

# Expose port 8001
# EXPOSE 8001

# Run the FastAPI app with Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]