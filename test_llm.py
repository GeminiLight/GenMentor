from dotenv import load_dotenv
load_dotenv()


from langchain.chat_models import init_chat_model



class LLMFactory:
    @staticmethod
    def get_llm(model: str, model_provider: str, **kwargs: dict):
        return init_chat_model(model=model, model_provider=model_provider, **kwargs)

together_llm = LLMFactory.get_llm(model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", model_provider="together", temperature=0)

print(together_llm.invoke("What is the capital of France?"))