import argparse
import json
import os
import glob
import fitz  # PyMuPDF
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"  # ~80MB, CPU-friendly


def extract_sections(doc):
    """Extracts sections/headings and their text from a PDF document."""
    font_stats = {}
    section_texts = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        size = span['size']
                        text = span['text'].strip()
                        if len(text) > 0:
                            font_stats[size] = font_stats.get(size, 0) + 1
    if not font_stats:
        return []
    # Heuristic: largest font sizes are headings
    font_sizes = sorted(font_stats.keys(), reverse=True)
    h1_size = font_sizes[0]
    h2_size = font_sizes[1] if len(font_sizes) > 1 else h1_size
    # Extract sections
    sections = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        size = span['size']
                        if not text or len(text) < 3:
                            continue
                        if abs(size - h1_size) < 0.1:
                            sections.append({
                                'level': 'H1',
                                'title': text,
                                'page': page_num,
                                'text': ''
                            })
                        elif abs(size - h2_size) < 0.1:
                            sections.append({
                                'level': 'H2',
                                'title': text,
                                'page': page_num,
                                'text': ''
                            })
    # Assign text to each section (simple: all text on the page)
    for section in sections:
        page = doc[section['page'] - 1]
        section['text'] = page.get_text()
    return sections


def load_persona_job(persona_path, job_path):
    with open(persona_path, 'r', encoding='utf-8') as f:
        persona_data = json.load(f)
    with open(job_path, 'r', encoding='utf-8') as f:
        job = f.read().strip()
    
    # Handle different persona structures
    if isinstance(persona_data.get('persona'), dict):
        # New structure: persona is a dictionary with role
        persona_str = persona_data['persona'].get('role', 'Unknown Role')
    else:
        # Old structure: persona is a string
        persona_str = persona_data.get('persona', 'Unknown Role')
    
    # Add focus areas if they exist
    focus_areas = persona_data.get('focus_areas', [])
    if focus_areas:
        persona_str += ". Focus: " + ", ".join(focus_areas)
    
    return persona_str, job


def process_documents(pdf_paths, persona_path, job_path, output_path):
    # Load persona/job
    persona_str, job_str = load_persona_job(persona_path, job_path)
    user_query = persona_str + ". Task: " + job_str
    # Load model
    model = SentenceTransformer(MODEL_NAME)
    user_emb = model.encode([user_query])
    extracted_sections = []
    subsection_analysis = []
    input_docs = []
    for pdf_path in pdf_paths:
        input_docs.append(os.path.basename(pdf_path))
        doc = fitz.open(pdf_path)
        sections = extract_sections(doc)
        if not sections:
            continue
        section_texts = [s['title'] + ". " + s['text'] for s in sections]
        section_embs = model.encode(section_texts)
        sims = cosine_similarity(user_emb, section_embs)[0]
        ranked = sorted(zip(sections, sims), key=lambda x: -x[1])
        for rank, (section, sim) in enumerate(ranked[:5], 1):
            extracted_sections.append({
                "document": os.path.basename(pdf_path),
                "page_number": section['page'],
                "section_title": section['title'],
                "importance_rank": rank
            })
            # Sub-section analysis: take most relevant paragraph
            paras = [p for p in section['text'].split('\n') if len(p.strip()) > 20]
            if paras:
                para_embs = model.encode(paras)
                para_sims = cosine_similarity(user_emb, para_embs)[0]
                best_idx = int(np.argmax(para_sims))
                subsection_analysis.append({
                    "document": os.path.basename(pdf_path),
                    "refined_text": paras[best_idx],
                    "page_number": section['page']
                })
    # Output JSON
    output = {
        "metadata": {
            "input_documents": input_docs,
            "persona": persona_str,
            "job_to_be_done": job_str,
            "processing_timestamp": datetime.utcnow().isoformat() + "Z"
        },
        "extracted_sections": extracted_sections,
        "subsection_analysis": subsection_analysis
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✓ Output written to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Persona-Driven Document Intelligence')
    parser.add_argument('--input', help='Input PDF file path (single file mode)')
    parser.add_argument('--input_dir', help='Input directory path (directory mode)')
    parser.add_argument('--persona', required=True, help='Persona definition JSON file')
    parser.add_argument('--job', required=True, help='Job-to-be-done text file')
    parser.add_argument('--output', required=True, help='Output JSON file path')
    args = parser.parse_args()

    if args.input:
        pdf_paths = [args.input]
    elif args.input_dir:
        pdf_paths = glob.glob(os.path.join(args.input_dir, '*.pdf'))
        if not pdf_paths:
            print(f"No PDFs found in {args.input_dir}, using sample PDF.")
            sample_pdf = os.path.join(args.input_dir, 'paper1.pdf')
            pdf_paths = [sample_pdf] if os.path.exists(sample_pdf) else []
    else:
        print("Error: Must specify --input or --input_dir")
        return 1
    if not pdf_paths:
        print("No PDF files to process.")
        return 1
    process_documents(pdf_paths, args.persona, args.job, args.output)
    return 0

if __name__ == '__main__':
    exit(main()) 