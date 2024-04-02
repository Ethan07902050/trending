import json
import random
import anthropic
from openai import OpenAI

prompt_template = """
There are some common topics among the following repositories delimited by triple backquotes.
Discover the key topics and introduce each one briefly in bullet points, along with some repositories as examples.

```
{text}
```

BULLET POINT TRENDING RESEARCH:
"""

file_path = '2024-04-02/repo_summary.json'

with open(file_path) as f:
    samples = json.load(f)
samples = [f'REPOSITORY_NAME: {repo_name}\nSUMMARY:{summary}\n' for repo_name, summary in samples.items()]
text = '\n'.join(samples)
# print(text)
prompt = prompt_template.format(text=text)

agent = 'claude'
if agent == 'gpt':
    client = OpenAI()
    response = client.chat.completions.create(
        # model="gpt-4-0125-preview",
        model="gpt-3.5-turbo-0125",
        messages=[
            {"role": "system", "content": "You are a professional in the field of artificial intelligence."},
            {"role": "user", "content": prompt},
        ]
    )

    print(response.choices[0].message.content)
    print(response.usage)
elif agent == 'claude':
    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    print(message.content[0].text)