# 🧾 DepoIndex

**DepoIndex** is an AI-powered tool designed to **automatically generate a table of contents** from legal deposition transcripts in PDF format. It uses **Google Gemini (LLM)** to extract structured topics along with their **page and line references**, then exports the results in multiple formats: `.json`, `.md`, and `.docx`.

---
## CLI syntax: 
    python build_toc.py --file <file_name> --out toc
    <file_name>  should be replaced with your files name
    use  "DepostionForPersisYu_LinkPDF.pdf" for this git repository 

## File descriptions

- build_toc.py: Main script to run the CLI
- CLI_run_screenshot.png: Screenshot of example CLI usage
- manual_validation_accuracy_score.png: screenshot of manual accuracy check
- cot_response.txt: Chain-of-thought output from Gemini
- DepostionForPersisYu_LinkPDF.pdf: Input deposition transcript
- Dockerfile: Containerized environment (optional)
- manual_validation_gemini_client.ipynb: Manual validation notebook
- README.md: This file
- requirements.txt: Python dependencies
- toc.docx: Generated TOC in Word format
- toc.json: Generated TOC in JSON format
- toc.md: Generated TOC in Markdown format
- validation_results.json: Output of the validation notebook

## 📌 Features

- Reads and processes legal PDFs page by page
-  Extracts structured topics using Gemini
-  Saves table of contents in:
  - `TableOfContents.json`
  - `TableOfContents.md`
  - `TableOfContents.docx`
-  Format:  
Topic — page <PageNumber>, line <LineNumber>



---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/your-username/depo-index.git
cd depo-index
2. Install Requirements
pip install -r requirements.txt

3. Set Up Google Gemini
You'll need a Gemini API key from Google AI Studio.


🧠 How It Works

## 📋 Preprocessing Steps

Before sending the transcript to the LLM, the following preprocessing steps are applied:

1. **PDF Reading**  
   - The PDF is loaded using `pypdf.PdfReader`.
   - Each page is processed sequentially.

2. **Text Extraction**  
   - Extract raw text from each page using `page.extract_text()`.

3. **Line Cleanup**  
   - Normalize whitespaces using regex: `re.sub(r"\s+", " ", line).strip()`.
   - Removes extra spaces and newlines to create clean input.

4. **Line Number Annotation**  
   - Each line is tagged with its **page number** and **line number** in the format:  
     `p<page_number>, l<line_number>: <line_text>`

5. **Formatted Prompt Construction**  
   - All cleaned lines are combined and passed into a structured LLM prompt template.  
   - This enables the LLM to return topics along with accurate page and line references.

6. **Final Prompt Example**  
   - Sample input to the LLM looks like:
     ```
     p2, l1: Counsel: When did you arrive at the location?
     p2, l2: Witness: Around 5 PM.
     ...
     ```


Prompt Formatting:

A formatted prompt is created to instruct Gemini to respond with:
[
  {
    "topic": "Topic Name",
    "page": 1,
    "line": 4
  },
  ...
]
LLM Response Parsing:

The Gemini response is parsed using json.loads.

Output Generation:

Markdown (.md)

DOCX (.docx)

JSON (.json)

All saved to your current directory as:

TableOfContents.json
TableOfContents.md
TableOfContents.docx
📄 Example Output (Markdown)

# Table of Contents

- Introduction to Witness — page 1, line 4  
- Contractual Obligations — page 2, line 15  
- Dispute Timeline — page 3, line 8  
- Closing Remarks — page 5, line 2

✅ Validation Notebook
File: manual_validation_gemini_client.ipynb

This notebook allows manual verification of each extracted topic using one Gemini API call. It also supports:

Optional chain-of-thought validation using Gemini

Sampling a few topics for human-in-the-loop checks

Result is saved to validation_results.json

Gemini is only called once to generate reasoning behind the predictions and this is cached in cot_response.txt. You can display it later upon request.