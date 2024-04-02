import json
import random
import anthropic
from openai import OpenAI

def load_jsonlines(file_path):
    samples = []
    f = open(file_path)
    for line in f:
        sample = json.loads(line.strip('\n'))
        samples.append(sample)
    f.close()
    return samples

def sample2str(sample):
    title = sample['title'].replace('\n', ' ')
    abstract = sample['abstract'].replace('\n', ' ')
    return f'Title: {title}\nAbstract:{abstract}\n'

prompt_template = """
There are some common topics among the following papers delimited by triple backquotes.
Discover the most important topics and introduce each one briefly in bullet points, along with some papers as examples.

```
{text}
```

TOPICS AND DESCRIPTIONS:
"""

file_path = 'papers/2024-01-selection.json'
agent = 'claude'

samples = load_jsonlines(file_path)
samples = [sample2str(sample) for sample in samples]
text = '\n'.join(samples)
prompt = prompt_template.format(text=text)

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