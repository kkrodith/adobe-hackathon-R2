import argparse
import json
import os
import glob
import fitz  # PyMuPDF
from collections import defaultdict


def extract_title(doc):
    # Try PDF metadata first
    title = doc.metadata.get('title')
    if title and title.strip():
        return title.strip()
    # Fallback: largest text on first page
    first_page = doc[0]
    blocks = first_page.get_text('dict')['blocks']
    max_size = 0
    title_text = ''
    for block in blocks:
        if block['type'] == 0:  # text block
            for line in block['lines']:
                for span in line['spans']:
                    if span['size'] > max_size and len(span['text'].strip()) > 5:
                        max_size = span['size']
                        title_text = span['text'].strip()
    return title_text


def extract_headings(doc):
    headings = []
    font_stats = defaultdict(list)  # font size -> [count, example text]
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if len(text) > 0:
                            font_stats[span['size']].append(text)
    # Heuristic: largest N font sizes are headings
    font_sizes = sorted(font_stats.keys(), reverse=True)
    if not font_sizes:
        return []
    h1_size = font_sizes[0]
    h2_size = font_sizes[1] if len(font_sizes) > 1 else h1_size
    # Now extract headings with their levels and page numbers
    outline = []
    for page_num, page in enumerate(doc, 1):
        blocks = page.get_text('dict')['blocks']
        for block in blocks:
            if block['type'] == 0:
                for line in block['lines']:
                    for span in line['spans']:
                        text = span['text'].strip()
                        if not text or len(text) < 3:
                            continue
                        size = span['size']
                        if abs(size - h1_size) < 0.1:
                            outline.append({'level': 'H1', 'text': text, 'page': page_num})
                        elif abs(size - h2_size) < 0.1:
                            outline.append({'level': 'H2', 'text': text, 'page': page_num})
    return outline


def process_single_pdf(pdf_path, output_path):
    """Process a single PDF file and save results to JSON"""
    try:
        doc = fitz.open(pdf_path)
        title = extract_title(doc)
        outline = extract_headings(doc)
        result = {
            'title': title,
            'outline': outline
        }
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Processed: {os.path.basename(pdf_path)} -> {os.path.basename(output_path)}")
        doc.close()
        return True
    except Exception as e:
        print(f"✗ Error processing {pdf_path}: {str(e)}")
        return False


def process_directory(input_dir, output_dir):
    """Process all PDF files in input directory"""
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist")
        return False
    
    # Find all PDF files
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in '{input_dir}'")
        return False
    
    print(f"Found {len(pdf_files)} PDF file(s) to process...")
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    for pdf_path in pdf_files:
        filename = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(output_dir, f"{filename}.json")
        
        if process_single_pdf(pdf_path, output_path):
            success_count += 1
    
    print(f"\nProcessing complete: {success_count}/{len(pdf_files)} files processed successfully")
    return success_count > 0


def main():
    parser = argparse.ArgumentParser(description='Extract title and outline from PDF files.')
    parser.add_argument('--input', help='Input PDF file path (single file mode)')
    parser.add_argument('--output', help='Output JSON file path (single file mode)')
    parser.add_argument('--input_dir', help='Input directory path (directory mode)')
    parser.add_argument('--output_dir', help='Output directory path (directory mode)')
    
    args = parser.parse_args()
    
    # Check if we're in single file mode or directory mode
    if args.input and args.output:
        # Single file mode
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' does not exist")
            return 1
        
        success = process_single_pdf(args.input, args.output)
        return 0 if success else 1
    
    elif args.input_dir and args.output_dir:
        # Directory mode
        success = process_directory(args.input_dir, args.output_dir)
        return 0 if success else 1
    
    else:
        print("Error: Must specify either --input/--output (single file) or --input_dir/--output_dir (directory)")
        parser.print_help()
        return 1


if __name__ == '__main__':
    exit(main()) 