# Hello Gemini

## How to get API key

- <https://console.cloud.google.com/welcome>에서 프로젝트를 확인한다.
- <https://console.cloud.google.com/projectcreate>에서 프로젝트를 생성한다.
- <https://aistudio.google.com/apikey>에서 키를 생성한다.

## How to set API key

- 생성된 키를 `.env` 파일에 저장한다.

```ini
GEMINI_API_KEY=insert_gemini_api_key_here
```

## Set-up

- Install `uv` from <https://docs.astral.sh/uv/getting-started/installation/>

```bash
uv python install
uv venv
uv pip install .
```

## Install Gemini CLI

```cmd
npm install -g @google/gemini-cli
```
