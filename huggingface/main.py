import requests
import json
import fire
import anthropic
from tqdm import tqdm
from bs4 import BeautifulSoup

def get_readme():
    url = 'https://huggingface.co/models?sort=downloads'
    resp = requests.get(url)
    outputs = {}

    if resp.status_code != 200:
        print('Cannot access huggingface!')
    else:
        soup = BeautifulSoup(resp.content, 'html.parser')
        models = soup.find_all('h4')
        for model in tqdm(models):
            model_id = model.getText()
            link = f'https://huggingface.co/{model_id}/raw/main/README.md'
            r = requests.get(link)
            outputs[model_id] = r.text

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
    prompt_1_path='prompt_1.txt',
    prompt_2_path='prompt_2.txt',
    output_path='model_summary.txt'
):
    readmes = get_readme()
    if len(readmes) == 0:
        exit()

    with open(prompt_1_path) as f:
        prompt_template_1 = f.read()

    with open(prompt_2_path) as f:
        prompt_template_2 = f.read()

    # stage 1
    samples = {}
    for model_name, readme in tqdm(readmes.items()):
        prompt = prompt_template_1.format(model_name=model_name, readme=readme)
        samples[model_name] = summarize(prompt)
        print(model_name)
        print(samples[model_name])

    # stage 2
    samples = [f'MODEL_NAME: {model_name}\nSUMMARY:{summary}\n' for model_name, summary in samples.items()]
    text = '\n'.join(samples)
    prompt = prompt_template_2.format(text=text)
    summary = summarize(prompt)
    print(summary)

    with open(output_path, 'w') as f:
        f.write(summary)

if __name__ == '__main__':
    fire.Fire(main)