# Approach Explanation: Persona-Driven Document Intelligence

## Overview
This system is designed to act as an intelligent document analyst, extracting and prioritizing the most relevant sections from a collection of documents based on a specific persona and their job-to-be-done. The approach is fully generalizable, allowing it to handle any set of input documents, persona definitions, and job descriptions, as required by the challenge brief.

## Input Handling
The system accepts the following inputs:
- **Document Collection:** A directory or list of PDF files containing the documents to be analyzed.
- **Persona Definition:** A JSON file describing the persona, including their role and (optionally) focus areas or expertise.
- **Job-to-be-Done:** A plain text file specifying the concrete task the persona needs to accomplish.

All input files are specified via command-line arguments, ensuring flexibility and generality. The system does not hardcode any filenames or content, and can process any valid input set provided in the correct format.

## Preprocessing and Query Construction
Upon execution, the system reads the persona and job files. The persona information (role and focus areas) is combined with the job description to form a unified user query. This query represents the information need of the persona in the context of the job-to-be-done.

## Document Section Extraction
Each PDF document is parsed to extract its sections. This is typically done by identifying section titles and their corresponding text content. The system processes each section, associating it with its page number and title, and extracts the full text for further analysis.

## Semantic Relevance Scoring
The core of the system leverages a pre-trained Sentence Transformer model (from the `sentence-transformers` library) to encode both the user query and the document sections into dense vector embeddings. The cosine similarity between the user query embedding and each section embedding is computed to assess relevance. Sections are ranked based on their similarity scores, and the top-ranked sections are selected as the most relevant to the persona's needs.

## Sub-section Analysis
For each top-ranked section, the system further analyzes its content by splitting it into paragraphs or sub-sections. Each paragraph is encoded and scored for relevance to the user query, allowing the system to extract the most pertinent refined text from within each section. This provides a more granular and focused analysis tailored to the persona's job.

## Output Generation
The results are compiled into a structured JSON file containing:
- **Metadata:** Input documents, persona, job-to-be-done, and processing timestamp.
- **Extracted Sections:** For each relevant section, the document name, page number, section title, and importance rank.
- **Sub-section Analysis:** For each top section, the most relevant refined text and its page number.

## Generalization and Extensibility
The system is designed to be domain-agnostic and can process any set of documents, personas, and jobs, provided in the specified formats. It does not require internet access at runtime and is optimized to run efficiently on CPU within the resource constraints specified by the challenge.

## Conclusion
This approach ensures that the most relevant information is surfaced for any persona and job, making the system highly adaptable and effective for a wide range of document intelligence tasks. 