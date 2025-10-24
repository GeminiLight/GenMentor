# GenMentor LLM Providers

This repo wraps LangChain's universal `init_chat_model` to let you switch models using a single `provider:model_id` string. This update adds first-class support for:

- vLLM servers via OpenAI-compatible endpoints
- Together AI API ("together"; tolerant to the common misspelling "togather")

## Quick usage

Python example:

```python
from base.llms import create_llm

# vLLM (OpenAI-compatible) — requires a running server
# Export VLLM_BASE_URL (default: http://localhost:8000/v1)
llm = create_llm(
    "vllm:llama3.1-8b-instruct",
    max_tokens=256,
)

# Together AI — requires TOGETHER_API_KEY
llm = create_llm(
    "together:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    temperature=0.2,
)

# You can also pass a custom base URL explicitly via model_kwargs
llm = create_llm(
    "together:meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
    model_kwargs={"base_url": "https://api.together.xyz/v1"},
)
```

Once you have an `llm`, you can use it like any LangChain chat model (e.g., `llm.invoke([...])`).

## Environment variables

General:

- GENMENTOR_DEFAULT_MODEL: default provider:model (default: `openai:gpt-4o-mini`)

Provider API keys:

- OPENAI_API_KEY
- AZURE_OPENAI_API_KEY
- ANTHROPIC_API_KEY
- GOOGLE_API_KEY (also used for `gemini:`)
- GROQ_API_KEY
- MISTRAL_API_KEY
- COHERE_API_KEY
- HUGGINGFACEHUB_API_TOKEN
- TOGETHER_API_KEY
- VLLM_API_KEY (optional; many vLLM servers accept an arbitrary token)

Base URLs:

- VLLM_BASE_URL (default: `http://localhost:8000/v1`)
- TOGETHER_BASE_URL (default: `https://api.together.xyz/v1`)

You can override base URLs per call using `model_kwargs={"base_url": "..."}`.

## Accepted identifiers

- OpenAI: `openai:gpt-4o-mini`
- Azure OpenAI: `azure:<deployment>` (also sets `AZURE_DEPLOYMENT` env var automatically)
- Together AI: `together:<model_id>` (also accepts `togather:<model_id>`)
- vLLM: `vllm:<model_id>`
- Ollama: `ollama:llama3.2`
- HuggingFace (pipeline): `prometheus` or `prometheus-eval/prometheus-7b-v2.0` via `create_hf_llm`

Some legacy shortcuts like `gpt4o-mini` or `llama3.2` are auto-normalized to the correct provider forms.

## Notes

- vLLM and Together are routed through the OpenAI-compatible path in LangChain, so they work by setting a `base_url` and API key.
- Initialization does not make network calls; actual requests happen on `invoke`/`astream`.
- You can add `tags` and `metadata` in `create_llm(..., tags=[...], metadata={...})`; they are applied via `.with_config(...)`.
