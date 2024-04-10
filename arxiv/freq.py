import anthropic
import json
import fire
import re
import pandas as pd
from pathlib import Path

def check_format(input_string):
    pattern = r'^\d{4}\.\d{5}$'
    if re.match(pattern, input_string):
        return True
    else:
        return False

def load_csai_papers_excel(data_path):
    df = pd.read_excel(data_path)
    csai_papers = []

    for index, row in df.iterrows():
        _id = row['連結'].split('/')[-1][:-2]
        if not check_format(_id):
            continue
        
        data_object = {
            'id': _id,
            'title': row['標題'].replace('\n ', ''),
        }
        csai_papers.append(data_object)

    return csai_papers

def find_json_object(input_string):
    start_index = input_string.find('{')
    end_index = input_string.rfind('}')

    if start_index != -1 and end_index != -1:
        json_string = input_string[start_index:end_index+1]
        try:
            json_object = json.loads(json_string)
            return json_object
        except json.JSONDecodeError:
            pass

    return None

def get_keywords(samples, prompt_template, num_keywords=10):
    titles = '\n'.join([sample['title'] for sample in samples])
    prompt = prompt_template.replace('{num}', str(num_keywords))
    prompt = prompt.replace('{titles}', titles)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )

    print(message.content[0].text)
    print(message.usage)
    
    keywords = find_json_object(message.content[0].text)
    return keywords

def main(
    data_path='arxiv_cs_papers_2024-04.xlsx',
    prompt_path='prompt_keyword.txt',
    output_path='',
    num_keywords=10
):
    samples = load_csai_papers_excel(data_path)
    print('# of papers:', len(samples))
    with open(prompt_path) as f:
        prompt_template = f.read()    

    keywords = get_keywords(samples, prompt_template, num_keywords)
    if keywords is not None:
        if output_path == '':
            output_path = Path(data_path).stem + '_keyword.json'
        with open(output_path, 'w') as f:
            json.dump(keywords, f, indent=2)
    else:
        print('cannot find json object from LLM response!')        

if __name__ == '__main__':
    fire.Fire(main)