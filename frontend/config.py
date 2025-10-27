backend_endpoint = "http://127.0.0.1:5000/"
# backend_endpoint = "http://57.152.82.155:8000/"
use_mock_data = False
llm_type_list = ["gpt4o", "llama", "deepseek"]
llm_label_map = {
    "gpt4o": "GPT-4o",
    "llama": "Llama3.2",
    "deepseek": "DeepSeek",
    "together": "Llama3.3-Turbo"
}
use_search = True