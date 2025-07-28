import pypdf
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords, wordnet 
from nltk.stem import WordNetLemmatizer
import re
import argparse
import google.genai as genai
from google.genai import types
import json
from docx import Document
from typing import List

# NLTK Downloads
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')    
nltk.download('omw-1.4')    

stopwords_set = set(stopwords.words('english'))   #stopword that will be removed

# Helper function for WordNetLemmatizer POS mapping
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN 

def processText(path:str):
    
    reader = pypdf.PdfReader(path)
    num_pages = reader.get_num_pages()
    inputText = ''

    for i in range(num_pages):
        end = False
        text = reader.get_page(i).extract_text()
        text = text.lower()                                                 #making text lowercase
        if re.search(pattern='witness signature', string=text):             # to check whether this is the final page
            end = True
        text = re.sub(pattern=r'\b\d{2}:\d{2}\b', string=text, repl='')  # removing timestamps
        text = re.sub(pattern=r"page (\d+)",repl='',string=text)    

        tokens = word_tokenize(text) #tokenized text

        #starting lemmatization, stemming could potentially reduce accuracy
        lemmatizer = WordNetLemmatizer()

        # POS tag tokens before lemmatizing them
        # Note: 'tokens' are currently raw, lowercased, and cleaned words from the page.
        # This pos_tag will generate tags based on these original forms.
        tagged_tokens_for_lemmatization = pos_tag(tokens) 
        lemmatized_words = []
        for word, tag in tagged_tokens_for_lemmatization:
            # Lemmatize using the mapped WordNet POS tag
            lemmatized_words.append(lemmatizer.lemmatize(word, pos=get_wordnet_pos(tag))) 
        
        tokens = lemmatized_words # Update 'tokens' with the lemmatized list
        # End Lemmatization Block

        pos_tags = pos_tag(tokens)  #removing unnecessary POS (This will re-tag the lemmatized tokens)
        pos_to_remove = {'DT', 'IN', 'CC'}      # Determiner, Preposition, Conjunction   (tokens   to be removed)
        filtered_tokens_pos = [word for word, tag in pos_tags if tag not in pos_to_remove and word not in stopwords_set and word not in {',',';',':'} ]
        text = f'\n PAGE_{i+1} \n'
        for str in filtered_tokens_pos:
            text = text + ' ' + str
        inputText = inputText + text
        if end:
            break                                                        # break if reached end
    return inputText

def promptLLM(processed_Text:str):
    prompt = f"""You are DepoIndex, an expert paralegal that labels *new* topics in deposition transcripts. Always reply in JSON ONLY. 
    I have provided a lemmetized text, and removed stop words. The text is a complete deposition transcript. 
    Every page begins with PAGE_(page number). Each line in the transcript starts with its line number (e.g., '1', '2', ..., '25'). Use this to find the starting point of each topic.
    Your job is to return a json in the structure following structure
    {{
        "topics": ["topics in order"]
        "page" : ["the page of the corresponding topic"]
        "line" : ["line number where the topic begins."]
    }}
    And i remind you, every page STARTS with the page number, every line starts with the line number. Re-use the **exact same topic label** (case-sensitive) if a new section appears similar in content or is a continuation of a previous topic. This maintains consistency in the output.
    These are a few examples.
    example 1 (
    input text = '''
        PAGE_1
        1 united state district court 2 southern district california 3 4 5 heather turrey oliver fiety ) jordan hernandez jeffrey ) 6 sazon individually ) behalf others ) 7 similarly situate ) ) 8 plaintiff ) ) 9 vs. ) case no. ) 3:20-cv-00697-dms ( ahg ) 10 vervent inc. fka first ) associate loan servicing ) 11 llc activate financial llc ) david johnson lawrence ) 12 chiavaro ) ) 13 defendant . ) ______________________________ ) 14 15 16 deposition persis yu 17 sacramento california 18 tuesday march 28 2023 19 20 21 22 report matthew sculatti csr . 13558 23 24 25 veritext legal solution 866 299-5127
        PAGE_2
        1 united state district court 2 southern district california 3 4 5 heather turrey oliver fiety ) jordan hernandez jeffrey ) 6 sazon individually ) behalf others ) 7 similarly situate ) ) 8 plaintiff ) ) 9 vs. ) case no. ) 3:20-cv-00697-dms ( ahg ) 10 vervent inc. fka first ) associate loan servicing ) 11 llc activate financial llc ) david johnson lawrence ) 12 chiavaro ) ) 13 defendant . ) ______________________________ ) 14 15 16 17 deposition persis yu take 18 matthew sculatti certified shorthand reporter 19 state california commence 1:15 p.m. 20 tuesday march 28 2023. deposition report 21 remotely veritext virtual technology . 22 23 24 25 veritext legal solution 866 299-5127
        PAGE_3
        1 appearance 2 3 4 plaintiff 5 blood hurst o'reardon llp 6 timothy g. blood attorney law 7 james m. davis attorney law 8 501 west broadway 9 suite 1490 10 san diego california 92101 11 tel ( 619 ) 338-1100 12 fax ( 619 ) 338-1101 13 tblood @ bholaw.com 14 jdavis @ bholaw.com 15 16 plaintiff 17 langer grogan diver pc 18 irv ackelsberg attorney law 19 1717 arch street 20 suite 4020 21 philadelphia pennsylvania 19103 22 tel ( 215 ) 320-5660 23 fax ( 215 ) 320-5703 24 iackelsberg @ langergrogan.com 25 veritext legal solution 866 299-5127'''
    output = {{
        "topics" : ["Case Title", "Deposition particulars","Appearences for deposition"]
        "page" : [1,1,3]
        "line" : [1,5,1]
        }}
    )
    example 2 (
    input text = '''
        PAGE_22
        1 'll refer vervent 2 first associate time 2011 ? 3 aware data -- 'm sorry 4 say ? 5 q sure . 6 aware regulation 7 violate access group transfer data 8 peak loan client vervent 2011 ? 9 's scope ask 10 look case n't -- n't 11 access document transfer 12 could n't make opinion rule 13 violate . 14 q okay . ever job relate 15 criminal law ? 16 yes . intern 17 district attorney 's office 2002 . 18 q extent work experience 19 relating criminal law ? 20 -- tangentially 21 experience work survivor domestic violence . 22 q okay . experience 23 criminal law ? 24 volunteer teen court 25 attorney rochester . veritext legal solution 866 299-5127 
        PAGE_23
        1 q okay . ? 2 recall 3 instance . 4 serve jury . 5 q ever job decide 6 someone would charge crime ? 7 . 8 q familiar -- familiarity 9 rico statute ? 10 -- -- generally aware rico 11 statute . 12 q ever job help 13 determine rico enterprise exist ? 14 work -- consumer attorney -- 15 position consider work others 16 consider rico violation 17 occur . 18 q ever experience 19 context student loan ? 20 case would -- would 21 student loan relate case . 's primary 22 area expertise . 23 q many time ? 24 small handful time . less half -- 25 less half dozen . veritext legal solution 866 299-5127
        PAGE_24
        1 q last time ? 2 could n't recall . 3 q mean five ten year ago ? 4 ? 5 last five ten year sure . 6 q report attached hereto 7 first exhibit deposition make finding 8 rico enterprise ? 9 ask provide legal opinion 10 rico enterprise . 11 q make finding respect 12 issue ? 13 -- scope 14 report . 15 q go -- 'm go go back 16 report . 'm -- 's paragraph 8 . see 17 're ? paragraph 8 longer 18 paragraph number . conscious decision ? 19 conscious decision . 20 q okay . happen . 'm try give 21 hard time . wonder 's 22 significance first part prefatory 23 rest different somehow -- 24 ? okay . 25 . veritext legal solution 866 299-5127
        PAGE_25
        1 q okay . thank . 2 provide -- initial background 3 provide overview high education for-profit 4 college . familiarity concept 5 for-profit college america take ? 6 . 7 q -- 's law for-profit 8 school correct ? 9 correct . 10 q 's law make profit either 11 correct ? 12 correct . 13 q firsthand experience 14 quality education -- itt ? 15 mr. blood say firsthand ? 16 mr. purcell yes . 17 witness never attend itt . 18 mr. purcell 19 q -- -- part -- work 20 ever anything analyze -- -- 21 level -- education ? 22 -- area expertise student 23 lending area would 've examine 24 regard itt -- debt student 25 incur . -- -- individual veritext legal solution 866 299-5127
        PAGE_28
        1 level -- -- represent individual borrower -- 2 -- 've represent small number itt 3 student however expertise look 4 broadly itt systemic problem 5 identify regulator also senate 6 committee look systemically issue 7 raise student loan borrower 8 context understand way itt lead 9 student debt . 10 q would fair say view itt 11 base -- material 've review 12 many occasion benefit itt education 13 outweigh burden debt student take ? 14 'm sorry ask one time ? 15 q sure . 16 -- view many occasion itt 17 student receive less benefit education 18 would commensurate amount student 19 debt take ? 20 view -- let rephrase . 21 base analysis material 22 -- public domain report itt 23 report rely show 24 student -- student receive 25 benefit promise itt veritext legal solution 866 299-5127
        PAGE_29
        1 lead take debt first place . 2 q -- 's opinion itt 3 diploma worthless correct ? 4 ... 5 mr. blood vague . 6 witness well yeah . mean think 7 n't really understand mean say 8 -- worthless . mean data suggest 9 know folk attend school -- folk attend 10 for-profit college get diploma 11 itt typically earn less even 12 high school diploma . 13 think 's also issue 14 student complete degree . itt 15 for-profit school extraordinarily high 16 rate . 17 mr. purcell 18 q uh-huh . 19 many -- large -- systemically 20 large number folk -- even one say 21 -- degree value -- -- n't -- 22 know data earnings know 23 data retention . n't -- 'm position 24 say educational quality example . 25 -- say economic outcome veritext legal solution 866 299-5127
        PAGE_30
        1 student attend itt typic- -- -- 2 statistically bad many folk attend 3 itt . 4 mr. purcell 5 q okay . 'm try unpack little 6 bit -- 7 sure . 8 q -- -- 're talk 9 statistic . 10 -- statistic aware 11 many -- percentage itt student end 12 get degree oppose get 13 degree ? 14 'll -- -- 'm go refer report 15 believe date . believe -- 16 senate help committee look specifically itt 17 look retention rate itt . 18 mr. blood ms. yu -- senate 19 committee ? n't catch . 20 witness -- -- 'm sorry . 21 senate help committee health education 22 labor pension committee . 23 mr. blood thank . 24 witness report -- 25 release report 2012 base two-year veritext legal solution 866 299-5127
        PAGE_31
        1 investigation number for-profit institution . 2 itt one school investigate . 3 part investigation release data regard 4 retention rate itt . 'm happy 'll give 5 moment take look pull number 6 . 7 mr. purcell 8 q sure . 9 appear put exact figure 10 retention rate -- report . n't 11 document senate help report . -- 12 metric besides retention important look 13 -- judge quality degree 14 quality -- borrower experience -- 15 student rather experience valuable experience 16 look default rate institution itt 17 notably high default rate indicate -- 18 good indicator student get 19 value -- value education 20 take loan get . 21 q okay . couple sort big-picture question . 22 one -- 23 sure . 24 q -- one -- opinion 25 degree itt worthless fair ? veritext legal solution 866 299-5127'''
    output = {{
        "topics" :["Experience in criminal law", "Knowledge about RICO statute","Experience in ITT institute(loans, student debt, education value)"]
        "page" :[24,25,27]
        "line": [14,8,13]
    }}
    )
    Make sure to check for line number. It MUST be between 1 and 25
    Page number will always be mentioned at start of each page. 
    
    Here is the actual input text:
    <<<
    {processed_Text}
    >>>

    Now extract topics and return ONLY the JSON output.
    """
    client = genai.Client(api_key="AIzaSyC1At4jLRY6zTVpJ120n214pwZUPH4-E-8")
    configuration = types.GenerateContentConfig(
        temperature=0.2,
        response_mime_type="application/json"     #to enforce JSON return
    )
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=configuration
    )
    print("Response generated from LLM")
    return response

# STARTING FUNCTION CALLS
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Table of Contents for a deposition PDF")
    parser.add_argument("--file", type=str, required=True, help="Path to the input PDF file")
    parser.add_argument("--out", type=str, required=True, help="Base name for output files (without extension)")

    args = parser.parse_args()
    inputText = processText(args.file)
    response = promptLLM(inputText)
    resultJSON = json.loads(response.text)

    # Save JSON
    with open(f"{args.out}.json", "w") as f_json:
        json.dump(resultJSON, f_json, indent=4)

    # Format for markdown and docx
    entries = [
        f"{topic} -------- page {page}, line {line}"
        for topic, page, line in zip(resultJSON["topics"], resultJSON["page"], resultJSON["line"])
    ]

    # Save Markdown
    with open(f"{args.out}.md", "w") as f_md:
        f_md.write("# Table of Contents\n\n")
        for entry in entries:
            f_md.write(f"- {entry}\n")

    # Save Word Document
    doc = Document()
    doc.add_heading("Table of Contents", level=1)
    for entry in entries:
        doc.add_paragraph(entry)
    doc.save(f"{args.out}.docx")

    print("Done: JSON, Markdown, and DOCX files saved.")
