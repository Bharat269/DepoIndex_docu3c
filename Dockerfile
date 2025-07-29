# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for API key (optional fallback)
ENV GOOGLE_API_KEY=your-fallback-api-key

# Default command (can be overridden)
CMD ["python", "build_toc.py", "--file", "DepostionForPersisYu_LinkPDF.pdf", "--out", "toc"]
