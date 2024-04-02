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

def in_date_range(paper_date, from_date, until_date):
    paper_date = str2date(paper_date)
    return from_date <= paper_date <= until_date

def is_category(category_str, target_category):
    cats = category_str.split()
    return target_category in cats

year = 2024
dates = [
    (datetime(year, 1, 1), datetime(year, 1, 31)),
    (datetime(year, 2, 1), datetime(year, 2, 28)),
    # (datetime(year, 3, 1), datetime(year, 3, 31)),
    # (datetime(year, 4, 1), datetime(year, 4, 30)),
    # (datetime(year, 5, 1), datetime(year, 5, 31)),
    # (datetime(year, 6, 1), datetime(year, 6, 30)),
    # (datetime(year, 7, 1), datetime(year, 7, 31)),
    # (datetime(year, 8, 1), datetime(year, 8, 31)),
    # (datetime(year, 9, 1), datetime(year, 9, 30)),
    # (datetime(year, 10, 1), datetime(year, 10, 31)),
    # (datetime(year, 11, 1), datetime(year, 11, 30)),
    # (datetime(year, 12, 1), datetime(year, 12, 31)),
]

datapath = 'arxiv-metadata-oai-snapshot.json'
csai_papers = [[] for _ in range(len(dates))]
metadata = get_metadata(datapath)

for paper in tqdm(metadata, total=2445865):
    paper = json.loads(paper)
    if is_category(paper['categories'], 'cs.AI'):
        for i in range(len(dates)):
            if in_date_range(paper['update_date'], dates[i][0], dates[i][1]):
                csai_papers[i].append(paper)

output_path = Path('papers')
output_path.mkdir(exist_ok=True)
for i in tqdm(range(len(dates))):
    filename = f'{year}-{i+1:02}.json'
    with open(output_path / filename, 'w') as f:
        for paper in csai_papers[i]:
            output_str = json.dumps(paper)
            f.write(f'{output_str}\n')