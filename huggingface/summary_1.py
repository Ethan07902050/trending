import json
import anthropic
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm

prompt_template = """
Given the following huggingface model name and readme delimited by triple backquotes, describe the model in 50 words.

```
MODEL_NAME: {model_name}
README: {readme}
```

DESCRIPTION IN 50 WORDS:
"""

root_path = Path('2024-04-02')
readme_path = root_path / 'models_readme.json'
output_path = root_path / 'models_summary.json'
with open(readme_path) as f:
    samples = json.load(f)

agent = 'gpt'
outputs = {}
for model_name, readme in tqdm(samples.items()):
    prompt = prompt_template.format(model_name=model_name, readme=readme)
    print(model_name)

    if agent == 'gpt':
        client = OpenAI()
        response = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a professional artificial intelligent researcher."},
                {"role": "user", "content": prompt},
            ]
        )

        summary = response.choices[0].message.content
    elif agent == 'claude':
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt},
            ]
        )
        summary = message.content[0].text

    outputs[model_name] = summary

with open(output_path, 'w') as f:
    json.dump(outputs, f, indent=2)