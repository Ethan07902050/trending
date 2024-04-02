import json
import anthropic
from pathlib import Path
from openai import OpenAI
from tqdm import tqdm

prompt_template = """
Given the following github repository name and readme delimited by triple backquotes, describe the repository in 50 words.

```
REPOSITORY_NAME: {repo_name}
README: {readme}
```

DESCRIPTION IN 50 WORDS:
"""

root_path = Path('2024-04-02')
readme_path = root_path / 'repo_readme.json'
output_path = root_path / 'repo_summary.json'
with open(readme_path) as f:
    samples = json.load(f)

agent = 'gpt'
outputs = {}
for repo_name, readme in tqdm(samples.items()):
    prompt = prompt_template.format(repo_name=repo_name, readme=readme)
    print(repo_name)

    if agent == 'gpt':
        client = OpenAI()
        response = client.chat.completions.create(
            # model="gpt-4-0125-preview",
            model="gpt-3.5-turbo-0125",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
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

    print(summary)
    outputs[repo_name] = summary

with open(output_path, 'w') as f:
    json.dump(outputs, f, indent=2)