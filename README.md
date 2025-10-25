# GenMentor

## Quickstart

### Installation

```bash
conda create -n gen-mentor python=3.12
pip install -r requirements.txt
```

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8010
```

```bash
curl -X POST "http://localhost:8000/chat-with-tutor" -H "Content-Type: application/json" -d '{
  "messages": "[{\"role\": \"user\", \"content\": \"Hello!\"}]",
  "learner_profile": "Learner profile information",
  "llm_type": "gpt-4o"
}'