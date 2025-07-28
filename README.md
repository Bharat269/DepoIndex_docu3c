# 🧾 DepoIndex

**DepoIndex** is an AI-powered tool designed to **automatically generate a table of contents** from legal deposition transcripts in PDF format. It uses **Google Gemini (LLM)** to extract structured topics along with their **page and line references**, then exports the results in multiple formats: `.json`, `.md`, and `.docx`.

---
## CLI syntax: 
    python script.py --file "your deposition pdf name"
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
<details> <summary>requirements.txt</summary>
regex
re
pypdf
nltk
google.genai
json
argparse
docx
typing
python-docx
jupyterlab
</details>
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