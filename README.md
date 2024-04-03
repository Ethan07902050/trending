# AI Trending Analysis

## Setup
1. Set up API key.
```
export ANTHROPIC_API_KEY='your-api-key-here'
```

2. Download arxiv paper metadata from [kaggle](https://www.kaggle.com/datasets/Cornell-University/arxiv/data) and place the json file in `arxiv`.

## Arxiv
```
cd arxiv
python main.py --data_path=arxiv-metadata-oai-snapshot.json --output_path=paper_summary.txt
```

## Github
```
cd github
python main.py --output_path=repo_summary.json
```

## Huggingface
```
cd huggingface
python main.py --output_path=model_summary.txt
```