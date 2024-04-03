import json
import time
import requests
import fire
import anthropic
from pathlib import Path
from datetime import datetime, timedelta
from tqdm import tqdm

def get_year_month_list():
    # Get current date and time
    current_datetime = datetime.now()

    # Initialize a list to store "year-month" strings
    year_month_list = []

    # Loop through the last 6 months
    for i in range(1, 7):
        # Calculate the date 6 months ago from the current date
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

def load_csai_papers(year_month_list, data_path, cache_path='paper.json'):
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

    return all_papers

def sample2str(sample):
    title = sample['title'].replace('\n', ' ')
    abstract = sample['abstract'].replace('\n', ' ')
    return f'Title: {title}\nAbstract:{abstract}\n'

def analyze(samples, prompt_template):
    samples = [sample2str(sample) for sample in samples]
    text = '\n'.join(samples)
    prompt = prompt_template.format(text=text)

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return message.content[0].text

def main(
    data_path='arxiv-metadata-oai-snapshot.json',
    cache_path='paper.json',
    prompt_path='prompt.txt',
    output_path='paper_summary.txt',
    paper_to_llm=30,
):
    year_month_list = get_year_month_list()
    csai_papers = load_csai_papers(year_month_list, data_path, cache_path=cache_path)
    csai_papers = get_citation_count(csai_papers, cache_path=cache_path)
    
    csai_papers.sort(key=lambda x: -x['citationCount'] if 'citationCount' in x else 0)
    csai_papers = csai_papers[:paper_to_llm]

    with open(prompt_path) as f:
        prompt_template = f.read()

    analysis = analyze(csai_papers, prompt_template)

    print(analysis)
    with open(output_path, 'w') as f:
        f.write(analysis)

if __name__ == '__main__':
    fire.Fire(main)