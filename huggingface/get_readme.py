import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup

url = 'https://huggingface.co/models?sort=downloads'
resp = requests.get(url)
soup = BeautifulSoup(resp.content, 'html.parser')

models = soup.find_all('h4')
outputs = {}
for model in tqdm(models):
    model_id = model.getText()
    link = f'https://huggingface.co/{model_id}/raw/main/README.md'
    r = requests.get(link)
    outputs[model_id] = r.text

with open('2024-04-02/models_readme.json', 'w') as f:
    json.dump(outputs, f, indent=2)