"""Local LLM client using Ollama for JSON and Python Code generation."""

import json
import requests
import re
from pydantic import BaseModel

class OllamaClient:
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        """
        Initialize the Ollama client.
        """
        self.model_name = model_name
        self.base_url = base_url
        print(f"Initialized Ollama client for model: {model_name}")

    def generate(self, prompt: str, system: str = "", temperature: float = 0.2, format: str = None, images: list = None) -> str:
        """Raw generation endpoint using Ollama API."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        if format:
            payload["format"] = format
        if images:
            payload["images"] = images
            
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "")
        except requests.exceptions.RequestException as e:
            print(f"[Ollama Error] Ensure the Ollama server is running! Error: {e}")
            raise e

    def generate_json(self, prompt: str, schema_model: type[BaseModel], max_retries: int = 3, images: list = None) -> dict:
        """
        Generates structured JSON following the provided Pydantic schema, with auto-retry.
        """
        
        system_prompt = (
            "You are an expert educational scriptwriter and Manim animator. "
            "You ALWAYS output raw, valid JSON. Never add conversational text. "
            "CRITICAL: Do NOT echo or output the JSON schema itself! You must output a JSON *instance* containing actual data that conforms to the schema."
        )
        
        schema_str = json.dumps(schema_model.model_json_schema(), indent=2)
        
        full_prompt = (
            f"{prompt}\n\n"
            f"Here is the JSON schema your output must conform to:\n```json\n{schema_str}\n```\n"
            f"IMPORTANT: Generate the actual Storyboard JSON data. Do NOT repeat the $defs or the schema structure!"
        )

        for attempt in range(max_retries):
            print(f"[LLM] Generating storyboard (Attempt {attempt + 1}/{max_retries})...")
            
            # Using Ollama's native JSON format feature mathematically guarantees valid JSON!
            raw_text = self.generate(full_prompt, system=system_prompt, temperature=0.4, format="json", images=images)
            
            try:
                data = json.loads(raw_text)
                
                # LLM robustness: If it generated a single Scene instead of a Storyboard, wrap it!
                if "scene_number" in data and "scenes" not in data:
                    data = {
                        "title": "Storyboard",
                        "target_audience": "Students",
                        "story_continuity_plan": "Continuous narrative.",
                        "scenes": [data]
                    }

                # Recursively lowercase all dictionary keys to fix LLM capitalization errors
                def lowercase_keys(obj):
                    if isinstance(obj, dict):
                        return {str(k).lower(): lowercase_keys(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [lowercase_keys(v) for v in obj]
                    else:
                        return obj
                
                return lowercase_keys(data)
            except json.JSONDecodeError as e:
                print(f"[Error] Failed to parse JSON on attempt {attempt + 1}.")
                # Simple auto-fix for missing brackets
                try:
                    if not raw_text.endswith("}"):
                        raw_text += "}"
                    
                    data = json.loads(raw_text)
                    
                    # LLM robustness check inside auto-fix
                    if "scene_number" in data and "scenes" not in data:
                        data = {
                            "title": "Storyboard",
                            "target_audience": "Students",
                            "story_continuity_plan": "Continuous narrative.",
                            "scenes": [data]
                        }

                    def lowercase_keys(obj):
                        if isinstance(obj, dict):
                            return {str(k).lower(): lowercase_keys(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [lowercase_keys(v) for v in obj]
                        else:
                            return obj
                    return lowercase_keys(data)
                except:
                    if attempt == max_retries - 1:
                        print(f"[Fatal] Failed to parse JSON after {max_retries} attempts. Last output:\n{raw_text}")
                        raise e
                    print("[Retry] Retrying generation to fix JSON syntax...")
                    continue


class HFVisionClient:
    def __init__(self, model_name: str = "Qwen/Qwen2-VL-7B-Instruct"):
        """
        Initialize the HuggingFace Vision client.
        Uses transformers and accelerate (device_map="auto") to span across GPUs.
        """
        import torch
        from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
        
        self.model_name = model_name
        print(f"Initializing HuggingFace Vision client for model: {model_name} (This may take a few minutes if downloading)")
        
        import torch
        from transformers import BitsAndBytesConfig
        
        # 8-bit quantization cuts the model weight footprint from 15GB to 7.5GB.
        # Combined with device_map="balanced", each GPU will only hold ~3.75GB of weights.
        # This leaves an enormous ~11GB of free space on GPU 0 for massive Concept text chunks.
        quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        self.model = Qwen2VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="balanced",
            quantization_config=quantization_config
        )
        self.processor = AutoProcessor.from_pretrained(model_name)

    def generate_json(self, prompt: str, schema_model: type[BaseModel], max_retries: int = 3, images: list = None) -> dict:
        """
        Generates structured JSON following the provided Pydantic schema using Qwen2-VL.
        """
        from qwen_vl_utils import process_vision_info
        
        system_prompt = (
            "You are an expert educational scriptwriter and Manim animator. "
            "You ALWAYS output raw, valid JSON. Never add conversational text. "
            "CRITICAL: Do NOT echo or output the JSON schema itself! You must output a JSON *instance* containing actual data that conforms to the schema."
        )
        
        schema_str = json.dumps(schema_model.model_json_schema(), indent=2)
        
        full_prompt = (
            f"{prompt}\n\n"
            f"Here is the JSON schema your output must conform to:\n```json\n{schema_str}\n```\n"
            f"IMPORTANT: Generate the actual Storyboard JSON data. Do NOT repeat the $defs or the schema structure!"
        )

        content = []
        if images:
            for b64 in images:
                # Aggressively cap max_pixels to ~800x600 equivalent. 
                # Attention VRAM scales quadratically with pixels. This prevents the 3.5GB OOM spike.
                content.append({
                    "type": "image", 
                    "image": f"data:image/png;base64,{b64}",
                    "max_pixels": 600 * 800
                })
        content.append({"type": "text", "text": full_prompt})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]

        text = self.processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text],
            images=image_inputs,
            videos=video_inputs,
            padding=True,
            return_tensors="pt",
        ).to("cuda")

        for attempt in range(max_retries):
            print(f"[HF Vision] Generating storyboard (Attempt {attempt + 1}/{max_retries})...")
            
            generated_ids = self.model.generate(**inputs, max_new_tokens=2048)
            generated_ids_trimmed = [
                out_ids[len(in_ids) :] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]
            raw_text = self.processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )[0]
            
            # Clean up JSON formatting if it added markdown tags
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            try:
                data = json.loads(raw_text)
                
                if "scene_number" in data and "scenes" not in data:
                    data = {
                        "title": "Storyboard",
                        "target_audience": "Students",
                        "story_continuity_plan": "Continuous narrative.",
                        "scenes": [data]
                    }

                def lowercase_keys(obj):
                    if isinstance(obj, dict):
                        return {str(k).lower(): lowercase_keys(v) for k, v in obj.items()}
                    elif isinstance(obj, list):
                        return [lowercase_keys(v) for v in obj]
                    else:
                        return obj
                
                try:
                    del inputs
                    del generated_ids
                    del generated_ids_trimmed
                    del image_inputs
                    del video_inputs
                except:
                    pass
                import gc; import torch
                torch.cuda.empty_cache(); gc.collect()
                return lowercase_keys(data)
            except json.JSONDecodeError as e:
                print(f"[Error] Failed to parse JSON on attempt {attempt + 1}.")
                try:
                    if not raw_text.endswith("}"):
                        raw_text += "}"
                    
                    data = json.loads(raw_text)
                    
                    if "scene_number" in data and "scenes" not in data:
                        data = {
                            "title": "Storyboard",
                            "target_audience": "Students",
                            "story_continuity_plan": "Continuous narrative.",
                            "scenes": [data]
                        }

                    def lowercase_keys(obj):
                        if isinstance(obj, dict):
                            return {str(k).lower(): lowercase_keys(v) for k, v in obj.items()}
                        elif isinstance(obj, list):
                            return [lowercase_keys(v) for v in obj]
                        else:
                            return obj
                    
                    try:
                        del inputs
                        del generated_ids
                        del generated_ids_trimmed
                        del image_inputs
                        del video_inputs
                    except:
                        pass
                    import gc; import torch
                    torch.cuda.empty_cache(); gc.collect()
                    return lowercase_keys(data)
                except:
                    if attempt == max_retries - 1:
                        print(f"[Fatal] Failed to parse JSON after {max_retries} attempts. Last output:\n{raw_text}")
                        raise e
                    print("[Retry] Retrying generation to fix JSON syntax...")
                    continue

    def unload(self):
        """Free VRAM after storyboard phase."""
        import gc
        import torch
        del self.model
        del self.processor
        torch.cuda.empty_cache()
        gc.collect()
        print("[HF Vision] Unloaded model and cleared VRAM.")
