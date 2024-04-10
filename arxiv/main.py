import json
import time
import requests
import fire
import anthropic
import re
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

def get_year_month_list():
    # Get current date and time
    current_datetime = datetime.now()

    # Initialize a list to store "year-month" strings
    year_month_list = []

    # Loop through the last 3 months
    for i in range(1, 4):
        # Calculate the date 3 months ago from the current date
        past_date = current_datetime - timedelta(days=30*i)
        
        # Extract year and month from the past date
        year = str(past_date.year)
        month = str(past_date.month)
        year_month_str = f'{year[2:]}{month.zfill(2)}'
        year_month_list.append(year_month_str)

    return year_month_list

def get_metadata(data_path):
    with open(data_path, 'r') as f:
        for line in f:
            yield line

def in_date_range(paper_id, year_month_list):
    return paper_id.split('.')[0] in year_month_list

def is_category(category_str, target_category):
    cats = category_str.split()
    return target_category in cats

def load_csai_papers_json(year_month_list, data_path, cache_path='paper.json'):
    if not Path(cache_path).exists():
        csai_papers = []
        metadata = get_metadata(data_path)

        for paper in tqdm(metadata):
            paper = json.loads(paper)
            if is_category(paper['categories'], 'cs.AI') and in_date_range(paper['id'], year_month_list):
                csai_papers.append(paper)
        
        with open(cache_path, 'w') as f:
            json.dump(csai_papers, f, indent=2)
    else:
        print('loading papers from cache...')
        with open(cache_path) as f:
            csai_papers = json.load(f)

    return csai_papers

def check_format(input_string):
    pattern = r'^\d{4}\.\d{5}$'
    if re.match(pattern, input_string):
        return True
    else:
        return False

def load_csai_papers_excel(data_path, cache_path='paper.json'):
    if not Path(cache_path).exists():
        df = pd.read_excel(data_path)
        
        csai_papers = []

        for index, row in df.iterrows():
            _id = row['連結'].split('/')[-1][:-2]
            if not check_format(_id):
                continue
            
            data_object = {
                'id': _id,
                'title': row['標題'],
                'abstract': row['簡介'],
            }
            csai_papers.append(data_object)
    else:
        print('loading papers from cache...')
        with open(cache_path) as f:
            csai_papers = json.load(f)

    return csai_papers

def get_citation_count(papers, batch_size=500, cache_path='paper.json'):
    paper_with_citation = [paper for paper in papers if 'citationCount' in paper]
    paper_without_citation = [paper for paper in papers if 'citationCount' not in paper]
    print(f'retrieving citations for {len(paper_without_citation)} papers')

    outputs = []
    for i in range(0, len(paper_without_citation), batch_size):
        print(f'batch #{i // 500 + 1}')
        batch_samples = paper_without_citation[i:min(len(paper_without_citation), i+batch_size)]
        ids = ['ARXIV:' + sample['id'] for sample in batch_samples]        
        r = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params={'fields': 'citationCount'},
            json={"ids": ids}
        )
        results = r.json()
        attempt = 1
        print(f'attempt #{attempt}')

        # api request could be blocked by semanticscholar
        # try again after 5 seconds
        while True:
            try:
                for sample, r in tqdm(zip(batch_samples, results)):
                    sample['citationCount'] = r['citationCount'] if r is not None else 0                    
                    outputs.append(sample)
                break
            except:
                time.sleep(5)
                r = requests.post(
                    'https://api.semanticscholar.org/graph/v1/paper/batch',
                    params={'fields': 'citationCount'},
                    json={"ids": ids}
                )
                results = r.json() 
                attempt += 1
                print(f'attempt #{attempt}')         

    if len(paper_without_citation) != 0:
        all_papers = outputs + paper_with_citation
        with open(cache_path, 'w') as f:
            json.dump(all_papers, f, indent=2)
    else:
        all_papers = paper_with_citation

    return all_papers

def sample2str(sample):
    title = sample['title'].replace('\n', '')
    abstract = sample['abstract'].replace('\n', '')
    return f'Title: {title}\nAbstract:{abstract}\n'

def analyze(samples, prompt_template):
    samples = [sample2str(sample) for sample in samples]
    text = '\n'.join(samples)
    prompt = prompt_template.replace('{text}', text)
    # print(prompt)
    print('sending request to claude...')

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return message.content[0].text

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

def main(
    data_path='arxiv-metadata-oai-snapshot.json',
    cache_path='paper.json',
    prompt_path='prompt_chinese.txt',
    output_path='2401_2403_summary_v2.json',
    paper_to_llm=30,
):
    # load paper metadata from jsonlines or excel
    data_path = Path(data_path)
    if data_path.suffix == '.json':
        year_month_list = get_year_month_list()
        csai_papers = load_csai_papers_json(year_month_list, data_path, cache_path=cache_path)
    elif data_path.suffix == '.xlsx':
        csai_papers = load_csai_papers_excel(data_path)
    csai_papers = get_citation_count(csai_papers, cache_path=cache_path)
    
    # sorting papers from highest citation count to lowest
    csai_papers.sort(key=lambda x: -x['citationCount'] if 'citationCount' in x else 0)
    csai_papers = csai_papers[:paper_to_llm]

    # calling LLM API
    with open(prompt_path) as f:
        prompt_template = f.read()
    analysis = analyze(csai_papers, prompt_template)
    print(analysis)

    # save output results
    analysis_json = find_json_object(analysis)
    if analysis_json is not None:
        if output_path == '':
            output_path = f"{Path(data_path).stem}_summary.json"

        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(analysis_json, f, indent=2, ensure_ascii=False)
    else:
        print('cannot find json object from LLM response!')

if __name__ == '__main__':
    fire.Fire(main)