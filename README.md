# ComfyUI Grok Chat

A ComfyUI custom node for sending text and optional image inputs to xAI Grok models. It supports system instructions, additional prompt text, conversation context, model selection, temperature, top-p, and seed controls.

## Install

Run these commands from your ComfyUI installation:

```bash
cd custom_nodes
git clone https://github.com/Elevenheights/ComfyUI-Grok-Chat.git comfyui_grok_chat
python -m pip install -r comfyui_grok_chat/requirements.txt
```

Set `XAI_API_KEY` in the environment used to start ComfyUI, then restart ComfyUI.

On the common RunPod ComfyUI template, the full custom-node path is `/workspace/ComfyUI/custom_nodes`.

## Node

The package registers `GrokChatNode`, displayed as **Grok Chat Node** in the **Grok Chat** category.

Inputs include:

- Prompt and optional additional text
- Grok model selection fetched from the xAI API
- Optional image or image batch
- Optional system instruction
- Context retention and maximum context controls
- Temperature, top-p, and seed

API keys are read only from environment variables and are not saved in ComfyUI workflow files.
