# GenMentor

GenMentor is an AI-powered personalized learning platform that creates adaptive learning experiences tailored to individual learners' needs, skill gaps, and goals. The system combines advanced AI technologies including Large Language Models, Retrieval-Augmented Generation (RAG), and intelligent tutoring systems to deliver comprehensive educational content.

## Features

- **AI Chatbot Tutor**: Interactive conversational learning with personalized responses
- **Skill Gap Identification**: Analyzes learner profiles and identifies knowledge gaps
- **Learning Goal Refinement**: Helps learners define and refine their educational objectives
- **Adaptive Learner Modeling**: Creates and updates detailed learner profiles
- **Personalized Resource Delivery**: Generates tailored learning content and materials
- **Learning Path Scheduling**: Creates structured learning sequences with session planning
- **Knowledge Point Exploration**: Deep-dives into specific topics with multiple perspectives
- **Document Integration**: Combines various knowledge sources into cohesive learning materials
- **Quiz Generation**: Creates personalized assessments to test understanding

## Architecture

The system is built with a modular architecture consisting of:

- **Core Modules**:
  - `ai_chatbot_tutor`: Conversational AI tutoring interface
  - `skill_gap_identification`: Analyzes and identifies learning gaps
  - `adaptive_learner_modeling`: Manages learner profiles and adaptation
  - `personalized_resource_delivery`: Creates customized learning content
  - `learner_simulation`: Simulates learner behaviors for testing

- **Base Components**:
  - `llm_factory`: Manages different LLM providers (DeepSeek, OpenAI, etc.)
  - `rag_factory`: Handles retrieval-augmented generation
  - `embedder_factory`: Manages text embedding models
  - `searcher_factory`: Integrates web search capabilities

- **Configuration**: Hydra-based configuration management with YAML files

## Quickstart

### Prerequisites

- Python 3.12+
- Conda or virtual environment

### Installation

```bash
# Create and activate virtual environment
conda create -n gen-mentor python=3.12
conda activate gen-mentor

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Core Learning Endpoints

#### Chat with AI Tutor

```bash
curl -X POST "http://localhost:5000/chat-with-tutor" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": "[{\"role\": \"user\", \"content\": \"Hello!\"}]",
    "learner_profile": "Learner profile information",
    "model_provider": "deepseek",
    "model_name": "deepseek-chat"
  }'
```

#### Refine Learning Goal

```bash
curl -X POST "http://localhost:5000/refine-learning-goal" \
  -H "Content-Type: application/json" \
  -d '{
    "learning_goal": "Learn machine learning",
    "learner_information": "Beginner with programming experience",
    "model_provider": "deepseek",
    "model_name": "deepseek-chat"
  }'
```

#### Identify Skill Gap (with CV upload)

```bash
curl -X POST "http://localhost:5000/identify-skill-gap" \
  -F "goal=Learn data science" \
  -F "cv=@path/to/cv.pdf" \
  -F "model_provider=deepseek" \
  -F "model_name=deepseek-chat"
```

#### Create Learner Profile

```bash
curl -X POST "http://localhost:5000/create-learner-profile-with-info" \
  -H "Content-Type: application/json" \
  -d '{
    "learning_goal": "Learn web development",
    "learner_information": "{\"experience\": \"beginner\", \"interests\": [\"frontend\", \"backend\"]}",
    "skill_gap": "{\"missing_skills\": [\"JavaScript\", \"CSS\"]}",
    "method_name": "genmentor",
    "model_provider": "deepseek",
    "model_name": "deepseek-chat"
  }'
```

#### Schedule Learning Path

```bash
curl -X POST "http://localhost:5000/schedule-learning-path" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_profile": "{\"skills\": [], \"goals\": [\"web development\"]}",
    "session_count": 10,
    "model_provider": "deepseek",
    "model_name": "deepseek-chat"
  }'
```

#### Generate Tailored Content

```bash
curl -X POST "http://localhost:5000/tailor-knowledge-content" \
  -H "Content-Type: application/json" \
  -d '{
    "learner_profile": "{\"level\": \"beginner\"}",
    "learning_path": "[{\"topic\": \"HTML Basics\"}]",
    "learning_session": "{\"current_topic\": \"HTML\"}",
    "use_search": true,
    "allow_parallel": true,
    "with_quiz": true
  }'
```

## Configuration

The application uses Hydra for configuration management. Key configuration files:

- `config/main.yaml`: Main application settings
- `config/default.yaml`: Default configurations for all modules
- Environment variables can override YAML settings

### Supported LLM Providers

- **DeepSeek** (default): `deepseek-chat`, `deepseek-coder`
- **OpenAI**: `gpt-4o`, `gpt-4o-mini`, `gpt-3.5-turbo`
- **Anthropic**: `claude-3-sonnet`, `claude-3-haiku`

### RAG and Search Configuration

The system supports multiple search providers:
- **DuckDuckGo**: Web search integration
- **ChromaDB**: Vector storage for document retrieval
- **Sentence Transformers**: Text embeddings

## Data Flow

1. **Learner Input**: CV upload, learning goals, or direct information
2. **Skill Analysis**: Identifies gaps between current skills and learning objectives
3. **Profile Creation**: Builds comprehensive learner profile with adaptive modeling
4. **Path Planning**: Generates personalized learning sequences
5. **Content Generation**: Creates tailored learning materials with optional quizzes
6. **Interactive Learning**: AI tutor provides conversational support throughout

## Development

### Project Structure

```
backend/
├── main.py                    # FastAPI application entry point
├── api_schemas.py            # Pydantic models for API requests
├── requirements.txt          # Python dependencies
├── config/                   # Configuration files
│   ├── main.yaml
│   ├── default.yaml
│   └── loader.py
├── base/                     # Core components and factories
│   ├── llm_factory.py
│   ├── rag_factory.py
│   ├── embedder_factory.py
│   └── search_rag.py
├── modules/                  # Feature modules
│   ├── ai_chatbot_tutor/
│   ├── skill_gap_identification/
│   ├── adaptive_learner_modeling/
│   ├── personalized_resource_delivery/
│   └── learner_simulation/
└── utils/                    # Utility functions
    ├── preprocess.py
    └── llm_output.py
```

### Adding New Features

1. Create a new module under `modules/`
2. Define schemas in `modules/your_module/schemas.py`
3. Implement agents in `modules/your_module/agents/`
4. Add prompts in `modules/your_module/prompts/`
5. Register endpoints in `main.py`
6. Update API schemas in `api_schemas.py`

### Testing

The project includes an `api_tester/` directory with testing utilities. Run tests using:

```bash
python -m pytest test_config.py
```

## Dependencies

Key dependencies include:
- **FastAPI**: Web framework
- **LangChain**: LLM orchestration
- **Hydra**: Configuration management
- **Pydantic**: Data validation
- **ChromaDB**: Vector database
- **Sentence Transformers**: Text embeddings
- **DuckDuckGo Search**: Web search

## License

This project is part of the GenMentor research initiative.

## Support

For issues and questions, please refer to the project documentation or create an issue in the repository.