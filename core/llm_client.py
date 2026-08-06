"""Local LLM client using llama_cpp for structured JSON generation."""

import json
from pydantic import BaseModel
try:
    from llama_cpp import Llama
except ImportError:
    Llama = None
    print("Warning: llama-cpp-python is not installed.")


class LocalLLMClient:
    def __init__(self, model_path: str, n_ctx: int = 8192, n_gpu_layers: int = -1):
        """
        Initialize the LlamaCPP client.
        n_gpu_layers=-1 attempts to offload all layers to GPU (useful for Qwen2.5 7B on 8GB+ VRAM).
        """
        if Llama is None:
            raise ImportError("llama-cpp-python is required. Install via prebuilt wheel: https://github.com/abetlen/llama-cpp-python")
            
        print(f"Loading local model from {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            verbose=False,
            # For JSON schema enforcement in llama.cpp (optional but helpful if supported in the build)
        )
        print("Model loaded successfully.")

    def generate_json(self, prompt: str, schema_model: type[BaseModel]) -> dict:
        """
        Generates structured JSON following the provided Pydantic schema.
        """
        
        system_prompt = (
            "You are an expert educational scriptwriter and Manim animator. "
            "You ALWAYS output raw, valid JSON inside a ```json code block. Never add conversational text."
        )
        
        schema_str = json.dumps(schema_model.model_json_schema(), indent=2)
        
        # Qwen ChatML template
        formatted_prompt = (
            f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt}\n\n"
            f"Here is the JSON schema you must follow:\n```json\n{schema_str}\n```\n"
            f"Return ONLY the requested JSON object.\n<|im_end|>\n"
            f"<|im_start|>assistant\n```json\n"
        )

        print("[LLM] Generating storyboard (this might take a minute)...")
        response = self.llm(
            formatted_prompt,
            max_tokens=4096,
            temperature=0.4,
            stop=["```\n<|im_end|>", "<|im_end|>"],
            echo=False
        )
        
        raw_text = "```json\n" + response['choices'][0]['text']
        
        import re
        match = re.search(r"```json\n(.*?)\n```", raw_text, re.DOTALL)
        if match:
            text = match.group(1).strip()
        else:
            text = raw_text.replace("```json", "").replace("```", "").strip()
            
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            print(f"[Error] Failed to parse JSON from LLM: \n{text}")
            try:
                if not text.endswith("}"):
                    text += "}"
                return json.loads(text)
            except:
                raise e
