import os
import requests
import json
import base64
import numpy as np
from PIL import Image
from io import BytesIO
import torch
from openai import OpenAI

def load_grok_models():
    api_key = os.getenv("XAI_API_KEY")
    fallback_models = ["grok-2-latest", "grok-2-vision-latest", "grok-vision-beta", "grok-beta", "grok-2-1212"]
    if not api_key:
        print("[comfyui_grok_chat] Warning: XAI_API_KEY environment variable not set. Using fallback models list.")
        return fallback_models
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://api.x.ai/v1/models", headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = [m['id'] for m in data.get('data', [])]
            if models:
                print(f"[comfyui_grok_chat] Successfully fetched {len(models)} models from Grok API.")
                return models
        else:
            print(f"[comfyui_grok_chat] Failed to fetch models: HTTP {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[comfyui_grok_chat] Error fetching grok models: {e}")
    return fallback_models

models_list = load_grok_models()

def estimate_tokens(history):
    total_chars = 0
    for msg in history:
        content = msg.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    total_chars += len(part.get("text", ""))
    # Simple heuristic: 1 token ~= 4 characters
    return total_chars // 4

class GrokChatNode:
    chat_history = []
    last_prompt = ""
    last_additional_text = ""
    last_image = None
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": (
                    "STRING",
                    {
                        "default": "Enter your prompt here. Use {additional_text} as a placeholder if needed.",
                        "multiline": True
                    }
                ),
                "additional_text": (
                    "STRING",
                    {
                        "default": "",
                        "multiline": True
                    }
                ),
                "model": (models_list, {"default": models_list[0] if models_list else "grok-2-latest"}),
                "max_context_length_tokens": ("INT", {"default": 8192, "min": 256, "max": 200000, "step": 1024}),
                "temperature": ("FLOAT", {"default": 0.8, "min": 0.0, "max": 2.0, "step": 0.05}),
                "top_p": ("FLOAT", {"default": 0.95, "min": 0.0, "max": 1.0, "step": 0.05}),
                "keep_context": ("BOOLEAN", {"default": True}),
                "seed": ("INT", {"default": 42, "min": 0, "max": 2147483647, "step": 1}),
            },
            "optional": {
                "image": ("IMAGE",),
                "system_instruction": ("STRING", {"default": "", "multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "execute"
    CATEGORY = "Grok Chat"

    def tensor_to_pil(self, img_tensors):
        def to_pil(img_tensor):
            arr = img_tensor.cpu().numpy() if hasattr(img_tensor, "cpu") else np.array(img_tensor)
            arr = np.squeeze(arr)
            if arr.ndim == 3 and arr.shape[0] == 3:
                arr = np.transpose(arr, (1, 2, 0))
            arr = np.clip(255.0 * arr, 0, 255).astype(np.uint8)
            return Image.fromarray(arr)
        
        if isinstance(img_tensors, (list, tuple)):
            return [to_pil(t) for t in img_tensors]
        elif hasattr(img_tensors, 'ndim') and img_tensors.ndim == 4:  # Batch tensor
            return [to_pil(t) for t in img_tensors]
        else:
            return to_pil(img_tensors)

    def encode_image(self, image):
        def encode_single(img):
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        if isinstance(image, list):
            return [encode_single(img) for img in image]
        else:
            return encode_single(image)

    def execute(self, prompt, additional_text, model, max_context_length_tokens, temperature, top_p, keep_context, seed, image=None, system_instruction=""):
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            return ("Error: XAI_API_KEY environment variable is not set.",)

        client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

        # Check if inputs (text or image) changed
        image_changed = False
        if (image is None) != (GrokChatNode.last_image is None):
            image_changed = True
        elif image is not None:
            # Check identity first, then content logic
            if image is not GrokChatNode.last_image:
                if hasattr(image, "shape") and hasattr(GrokChatNode.last_image, "shape"):
                    if image.shape != GrokChatNode.last_image.shape or not torch.equal(image, GrokChatNode.last_image):
                        image_changed = True
                else:
                    image_changed = True

        inputs_changed = (prompt != GrokChatNode.last_prompt) or (additional_text != GrokChatNode.last_additional_text) or image_changed
        
        GrokChatNode.last_prompt = prompt
        GrokChatNode.last_additional_text = additional_text
        GrokChatNode.last_image = image

        if "{additional_text}" in prompt:
            full_user_text = prompt.replace("{additional_text}", additional_text)
        elif additional_text.strip():
            full_user_text = prompt + "\n\n" + additional_text
        else:
            full_user_text = prompt

        print(f"[comfyui_grok_chat] Request: Model='{model}', Temp={temperature}, KeepContext={keep_context}")

        if not keep_context:
            self.chat_history.clear()

        # Check and enforce max context length based on estimated tokens
        current_tokens = estimate_tokens(self.chat_history)
        if current_tokens > max_context_length_tokens:
            print(f"[comfyui_grok_chat] Context length exceeded ({current_tokens} > {max_context_length_tokens} tokens). Resetting history.")
            self.chat_history.clear()

        is_one_more = not inputs_changed and keep_context and len(self.chat_history) > 0
        if is_one_more:
            augmented_prompt = "Please provide one more response based on the previous prompt and context."
        else:
            augmented_prompt = full_user_text

        messages = []
        if system_instruction.strip():
            messages.append({"role": "system", "content": system_instruction.strip()})

        if keep_context and self.chat_history:
            messages.extend(self.chat_history)

        b64_list = None
        if image is not None and not is_one_more:
            pil_images = self.tensor_to_pil(image)
            b64_list = self.encode_image(pil_images)
            if isinstance(b64_list, str):
                b64_list = [b64_list]

        if b64_list:
            user_content = [{"type": "text", "text": augmented_prompt}]
            for b64 in b64_list:
                user_content.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}})
            messages.append({"role": "user", "content": user_content})
            current_message_for_history = {"role": "user", "content": user_content}
        else:
            messages.append({"role": "user", "content": augmented_prompt})
            current_message_for_history = {"role": "user", "content": augmented_prompt}

        try:
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                top_p=top_p,
                seed=seed
            )
            output_text = completion.choices[0].message.content

            if keep_context:
                self.chat_history.append(current_message_for_history)
                self.chat_history.append({"role": "assistant", "content": output_text})

            return (output_text,)
        except Exception as e:
            print(f"[comfyui_grok_chat] Error during generation: {e}")
            return (f"API Error: {e}",)

NODE_CLASS_MAPPINGS = {
    "GrokChatNode": GrokChatNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "GrokChatNode": "Grok Chat Node"
}
