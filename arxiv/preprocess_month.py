import json
from tqdm import tqdm
from datetime import datetime
from pathlib import Path

def get_metadata(datapath):
    with open(datapath, 'r') as f:
        for line in f:
            yield line

def str2date(s):
    year, month, day = list(map(int, s.split('-')))
    return datetime(year, month, day)

def in_date_range(paper_id, year, month):
    return paper_id.split('.')[0] == f'{year}{month:02}'

def is_category(category_str, target_category):
    cats = category_str.split()
    return target_category in cats

year = 24
month = 3

datapath = 'arxiv-metadata-oai-snapshot.json'
csai_papers = []
metadata = get_metadata(datapath)

for paper in tqdm(metadata, total=2445865):
    paper = json.loads(paper)
    if is_category(paper['categories'], 'cs.AI') and in_date_range(paper['id'], year, month):
        csai_papers.append(paper)

print(len(csai_papers))

output_path = Path('papers')
output_path.mkdir(exist_ok=True)
filename = f'20{year}-{month:02}.json'
with open(output_path / filename, 'w') as f:
    for paper in csai_papers:
        output_str = json.dumps(paper)
        f.write(f'{output_str}\n')