
import requests
import fitz
import re
import pandas as pd
import os

def download_pdf(url):
    filename = url.split('/')[-1]
    if not os.path.exists(filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
    return filename

def extract_data(pdf_path):
    doc = fitz.open(pdf_path)
    first_page_text = doc[0].get_text()
    first_page_text = re.sub('\s+', ' ', first_page_text)
    sentences = first_page_text.replace('\n', ' ').split('.')
    sentences = [sentence.strip() for sentence in sentences]

    for i in range(len(sentences) - 1):
        current_sentence = sentences[i]

        if "residents" in current_sentence:
            next_sentence = sentences[i + 1] if i + 1 < len(sentences) else ""
            next_sentence = re.sub('\s+', ' ', next_sentence).strip()
            return f"{current_sentence}.{next_sentence}."

    return "Phrase not found"

base_url = "https://www.nirsonline.org/wp-content/uploads/2023/01/pensionomics2023_{}.pdf"
base_url_2021 = "https://www.nirsonline.org/wp-content/uploads/2021/01/pensionomics2021_{}.pdf"

state_abbreviations = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

state_abbreviations_2021 = [item.lower() for item in state_abbreviations]

# Generate URLs for all states
urls = [base_url_2021.format(state) for state in state_abbreviations_2021]

pattern = r"In (\d{4}), ([\d,]+) residents of ([A-Za-z ]+) received a total\s+of (\$\d+(\.\d+)?\s+(billion|million)) in pension benefits"

sentences = []
for url in urls:
    pdf_path = download_pdf(url)
    sentence = extract_data(pdf_path)
    sentences.append(sentence)


data = []

for sentence in sentences:
    match = re.search(pattern, sentence)
    if match:
        # create a dictionary for each match, append to the list data
        data.append({
            'year': match.group(1),
            'residents': match.group(2),
            'state': match.group(3).strip(),
            'amount': match.group(4),
            'sentence': sentence
    })
    else:
        print(f'{sentence} "not found"')


df = pd.DataFrame(data)

df.to_csv('residents_received_pensions_2018.csv')
print(df)