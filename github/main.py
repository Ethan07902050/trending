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

def summarize(prompt):
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    summary = message.content[0].text
    return summary    

def main(
    prompt_1_path='prompt_1.txt',
    prompt_2_path='prompt_2.txt',
    readme_path='readme.json',
    output_path='repo_summary.json'
):
    readmes = get_readme()
    if len(readmes) == 0:
        exit()

    with open(prompt_1_path) as f:
        prompt_template_1 = f.read()

    with open(prompt_2_path) as f:
        prompt_template_2 = f.read()

    # stage 1
    outputs = {}
    for repo_name, readme in tqdm(readmes.items()):
        prompt = prompt_template_1.format(repo_name=repo_name, readme=readme)
        summary = summarize(prompt)
        outputs[repo_name] = summary
        print(repo_name)
        print(summary)

    with open(readme_path, 'w') as f:
        json.dump(outputs, f, indent=2)

    # stage 2
    samples = [f'REPO_NAME: {repo_name}\nSUMMARY: {summary}\n' for repo_name, summary in outputs.items()]
    text = '\n'.join(samples)
    prompt = prompt_template_2.replace('{text}', text)
    print('sending request to claude...')
    summary = summarize(prompt)
    print(prompt)
    print('-' * 50)
    print(summary)

    # save as json
    summary_json = find_json_object(summary)
    if summary_json is not None:
        with open(output_path, 'w', encoding='utf8') as f:
            json.dump(summary_json, f, indent=2, ensure_ascii=False)
    else:
        print('cannot find json object from LLM response!')

if __name__ == '__main__':
    fire.Fire(main)