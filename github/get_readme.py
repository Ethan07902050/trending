import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup

url = 'https://github.com/trending?since=monthly'
resp = requests.get(url)
soup = BeautifulSoup(resp.content, 'html.parser')

outputs = {}
tags = soup.find_all('h2', {'class': 'lh-condensed'})
for tag in tqdm(tags):
    repo_name = tag.a['href'][1:]
    links = [
        f'https://raw.githubusercontent.com/{repo_name}/main/README.md',
        f'https://raw.githubusercontent.com/{repo_name}/main/readme.md',
        f'https://raw.githubusercontent.com/{repo_name}/master/README.md',
        f'https://raw.githubusercontent.com/{repo_name}/master/readme.md',
    ]

    for link in links:
        r = requests.get(link)
        if r.status_code == 200:
            outputs[repo_name] = r.text
            break

with open('2024-04-02/repo_readme.json', 'w') as f:
    json.dump(outputs, f, indent=2)
    