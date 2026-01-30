FROM python:3.10-slim

# System updates
RUN apt-get update && apt-get install -y ffmpeg python3-pip

WORKDIR /app
COPY . .

# Install requirements
RUN pip install --no-cache-dir -r requirements.txt

# Start command
CMD ["python3", "main.py"]
