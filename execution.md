# Execution Instructions

## Local Development (Single File Mode)

To run the PDF extraction tool on a single file:

```
python main.py --input input/sample.pdf --persona input/persona.json --job input/job.txt --output output/result.json
```

- Replace `input/sample.pdf` with your input PDF file path
- Replace `output/result.json` with your desired output JSON file path

## Docker Execution (Directory Mode)

The tool is designed to run in a Docker container and process all PDFs in a directory:

```
python main.py --input_dir /app/input --persona /app/input/persona.json --job /app/input/job.txt --output /app/output/result.json
```

This will:
- Process all PDF files in `/app/input`
- Generate corresponding JSON files in `/app/output`
- Each `filename.pdf` produces `filename.json`

## Requirements
- Python 3.10 or 3.11 (PyMuPDF compatibility)
- Install dependencies with:
  ```
  pip install -r requirements.txt
  ```

## Docker Build and Run
```bash
# Build the image
docker build --platform linux/amd64 -t pdf-extractor:latest

# Run the container
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```
