import requests
import json
import fire
import anthropic
from tqdm import tqdm
from bs4 import BeautifulSoup

def get_readme():
    url = 'https://github.com/trending?since=monthly'
    resp = requests.get(url)
    outputs = {}

    if resp.status_code != 200:
        print('Cannot access github!')
    else:
        soup = BeautifulSoup(resp.content, 'html.parser')        
        tags = soup.find_all('h2', {'class': 'lh-condensed'})
        print('retrieving repo readme...')
        for tag in tqdm(tags):
            repo_name = tag.a['href'][1:] # remove preceding '/'
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

    return outputs

def summarize(prompt):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    summary = message.content[0].text
    return summary    

def main(
    prompt_path='prompt.txt',
    output_path='repo_summary.json'
):
    readmes = get_readme()
    if len(readmes) == 0:
        exit()

    with open(prompt_path) as f:
        prompt_template = f.read()

    outputs = {}
    for repo_name, readme in readmes.items():
        prompt = prompt_template.format(repo_name=repo_name, readme=readme)
        summary = summarize(prompt)
        outputs[repo_name] = summary
        print(repo_name)
        print(summary)

    with open(output_path, 'w') as f:
        json.dump(outputs, f, indent=2)

if __name__ == '__main__':
    fire.Fire(main)