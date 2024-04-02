import json
import requests
import time
from pathlib import Path
from tqdm import tqdm

def load_jsonlines(file_path):
    samples = []
    f = open(file_path)
    for line in f:
        sample = json.loads(line.strip('\n'))
        samples.append(sample)
    f.close()
    return samples

def get_citation_count(samples, batch_size=500):
    outputs = []
    for i in range(0, len(samples), batch_size):
        batch_samples = samples[i:min(len(samples), i+batch_size)]
        ids = ['ARXIV:' + sample['id'] for sample in batch_samples]        
        r = requests.post(
            'https://api.semanticscholar.org/graph/v1/paper/batch',
            params={'fields': 'citationCount'},
            json={"ids": ids}
        )
        results = r.json()
        attempt = 1

        while True:
            try:
                for sample, r in tqdm(zip(batch_samples, results)):
                    if r is not None:
                        sample['citationCount'] = r['citationCount']
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
                print('attempt:', attempt)          

    return outputs

if __name__ == '__main__':
    year = 2024
    for month in range(3, 4):
        print(month)
        file_path = f'papers/{year}-{month:02}.json'
        samples = load_jsonlines(file_path)
        outputs = get_citation_count(samples)

        with open(file_path, 'w') as f:
            for sample in outputs:
                output_str = json.dumps(sample)
                f.write(f'{output_str}\n')
        