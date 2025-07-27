FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
# COPY input ./input
# COPY output ./output

# Entrypoint: process all PDFs in /app/input and write to /app/output
CMD ["python", "main.py", "--input_dir", "/app/input", "--persona", "/app/input/persona.json", "--job", "/app/input/job.txt", "--output", "/app/output/result.json"]