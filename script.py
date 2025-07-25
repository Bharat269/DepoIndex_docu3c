import regex as re
from pypdf import PageObject, PdfReader
import os
import google.generativeai as genai
import json
import time

os.environ["GOOGLE_API_KEY"] = "AIzaSyC1At4jLRY6zTVpJ120n214pwZUPH4-E-8"  # replace this or use dotenv
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# Page Cleaning
def processPage(page: PageObject):
    text = page.extract_text()
    if not text:
        return None, None

    # Extract page number
    match = re.search(pattern=r"Page (\d+)", string=text)
    if not match:
        return None, None
    page_number = int(match.group(1))

    # Remove timestamps (e.g., 10:32)
    text = re.sub(pattern=r'\b\d{2}:\d{2}\b', string=text, repl='')

    lines = text.split('\n')
    # Keep only numbered lines (e.g., "12 So tell me...")
    filtered_lines = [l for l in lines if re.search(r'^\d{1,2}\s', l)]
    newtext = '\n'.join(filtered_lines)

    return newtext, page_number

# to find at what line number the topic starts
def find_line_number(text_block: str, starting_line: str):
    for l in text_block.split('\n'):
        if l.strip().startswith(starting_line.strip()):
            linenum = l.split()[0]
            return int(linenum.strip())
    return None

# Gemini LLM Call 
def promptLLM(last_topic: str, page_text: str) -> dict:
    model = genai.GenerativeModel("gemini-2.0-flash")

    prompt = f"""
You are analyzing a legal deposition.

Last known topic: "{last_topic}"
List topics with minor differences as well, such as appearences and introudction or so.

Here is the next page of the transcript:
---
{page_text}
---

If a new subject begins, respond ONLY with:
{{
  "boolTopicFound": true,
  "newtopicname": "Short title of the new topic",
  "startinglineoftopic": "The exact first line where this new topic starts"
}}

If it is the same topic as the previous one, respond ONLY with:
{{
  "boolTopicFound": false,
  "newtopicname": "",
  "startinglineoftopic": ""
}}

Do NOT explain anything. Return JSON only.
"""

    try:
        response = model.generate_content(prompt)
        llm_reply = response.text.strip()

        # Extract just the JSON part if anything extra is returned
        json_start = llm_reply.find('{')
        json_end = llm_reply.rfind('}') + 1
        cleaned_json = llm_reply[json_start:json_end]

        return json.loads(cleaned_json)

    except Exception as e:
        print("Error in Gemini response:", e)
        print("Full Gemini output:", response.text if 'response' in locals() else 'None')
        return {
            'boolTopicFound': False,
            'newtopicname': '',
            'startinglineoftopic': ''
        }

# --- Main Loop ---
lastTopic = ''
topics = []

reader = PdfReader('DepostionForPersisYu_LinkPDF.pdf')
number_of_pages = reader.get_num_pages()

for i in range(number_of_pages):
    page = reader.get_page(i)
    newtext, page_number = processPage(page)

    if newtext and page_number:
        output = promptLLM(last_topic=lastTopic, page_text=newtext)

        if output.get('boolTopicFound'):
            linenum = find_line_number(newtext, output['startinglineoftopic'])

            if linenum is not None:
                new_topic_data = {
                    "topic": output['newtopicname'],
                    "page_start": page_number,
                    "line_start": linenum
                }
                topics.append(new_topic_data)
                lastTopic = output['newtopicname']
    time.sleep(1)

# Save results
with open('toc.md', 'w') as f:
    f.write("# Deposition Table of Contents\n\n")
    for item in topics:
        line = f"{item['topic']} ··· Page {item['page_start']} · Line {item['line_start']}\n"
        f.write(line)
print("Processing complete.")
print(topics)
