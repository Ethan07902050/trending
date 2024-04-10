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
        print('retrieving model readme from huggingface...')
        soup = BeautifulSoup(resp.content, 'html.parser')
        models = soup.find_all('h4')
        for model in tqdm(models):
            model_id = model.getText()
            link = f'https://huggingface.co/{model_id}/raw/main/README.md'
            r = requests.get(link)
            outputs[model_id] = r.text

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
    output_path='model_summary.json'
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

    with open(readme_path, 'w') as f:
        json.dump(samples, f, indent=2)

    # stage 2
    samples = [f'MODEL_NAME: {model_name}\nSUMMARY:{summary}\n' for model_name, summary in samples.items()]
    text = '\n'.join(samples)
    prompt = prompt_template_2.replace('{text}', text)
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