# Persona-Driven Document Intelligence

This tool extracts and prioritizes the most relevant sections from a collection of PDF documents based on a specific persona and their job-to-be-done. It outputs a structured JSON with metadata, extracted sections, and sub-section analysis.

## Features
- Extracts document title and outline
- Persona and job-to-be-done conditioning
- Ranks and prioritizes relevant sections
- Sub-section analysis with refined text
- Outputs to JSON in the required challenge format
- Fast: ≤60 seconds for 3-5 documents
- Offline, CPU-only, model size ≤1GB
- Supports both single file and directory processing modes

## Usage

### Single File Mode
```
python main.py --input input/sample.pdf --persona input/persona.json --job input/job.txt --output output/result.json
```

### Directory Mode (Docker)
```
python main.py --input_dir /app/input --persona /app/input/persona.json --job /app/input/job.txt --output /app/output/result.json
```

## Requirements
- Python 3.10 or 3.11
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```

## Docker Execution
The tool is designed to run in a Docker container:
- Processes all PDFs in `/app/input` directory
- Persona and job files in `/app/input`
- Generates a single output JSON in `/app/output`

## Input/Output
- Place input PDFs in the `input/` directory
- Place `persona.json` and `job.txt` in the `input/` directory
- Output JSON file will be saved in the `output/` directory

## Example Output Format
```json
{
  "metadata": {
    "input_documents": ["doc1.pdf", "doc2.pdf"],
    "persona": "PhD Researcher in Computational Biology",
    "job_to_be_done": "Prepare a comprehensive literature review focusing on methodologies, datasets, and performance benchmarks",
    "processing_timestamp": "2024-06-01T12:00:00Z"
  },
  "extracted_sections": [
    {
      "document": "doc1.pdf",
      "page_number": 3,
      "section_title": "Graph Neural Networks Overview",
      "importance_rank": 1
    }
  ],
  "subsection_analysis": [
    {
      "document": "doc1.pdf",
      "refined_text": "Graph neural networks (GNNs) are a class of neural networks...",
      "page_number": 3
    }
  ]
}
```

## Sample Input/Output
- See `input/` and `output/` directories for sample files. 