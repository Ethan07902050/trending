import json

def load_jsonlines(file_path):
    samples = []
    f = open(file_path)
    for line in f:
        sample = json.loads(line.strip('\n'))
        samples.append(sample)
    f.close()
    return samples

year = 2024
samples = []
for month in range(1, 4):
    file_path = f'papers/{year}-{month:02}.json'
    samples += load_jsonlines(file_path)

samples.sort(key=lambda x: -x['citationCount'] if 'citationCount' in x else 0)
samples = samples[:30]

with open(f'papers/{year}-01-selection.json', 'w') as f:    
    for sample in samples:
        output_str = json.dumps(sample)
        f.write(f'{output_str}\n')