# ComfyUI Grok Chat

A ComfyUI custom node for sending text and optional image inputs to xAI Grok models. It supports system instructions, additional prompt text, conversation context, model selection, temperature, top-p, and seed controls.

## Install

Run these commands from your ComfyUI installation:

```bash
cd custom_nodes
git clone https://github.com/Elevenheights/ComfyUI-Grok-Chat.git comfyui_grok_chat
python -m pip install -r comfyui_grok_chat/requirements.txt
```

On the common RunPod ComfyUI template, the full custom-node path is `/workspace/ComfyUI/custom_nodes`.

## Add the xAI key on RunPod

Open one file:

```bash
nano /workspace/ComfyUI/custom_nodes/comfyui_grok_chat/xai_api_key.txt
```

Paste only your xAI key, then press `Ctrl+O`, `Enter`, and `Ctrl+X`. Restart
ComfyUI so the model list reloads. The key file is ignored by Git and is never
saved in a workflow.

If the repository was cloned using a different folder name, edit
`xai_api_key.txt` inside that folder instead. Advanced installations may still
use the `XAI_API_KEY` environment variable; it takes priority over the file.

Keep ComfyUI and this custom node under `/workspace` so the key file survives a
RunPod pod restart. Do not put the key in a workflow or commit it to GitHub.

## Node

The package registers `GrokChatNode`, displayed as **Grok Chat Node** in the **Grok Chat** category.

Inputs include:

- Prompt and optional additional text
- Grok model selection fetched from the xAI API
- Optional image or image batch
- Optional system instruction
- Context retention and maximum context controls
- Temperature, top-p, and seed

The API key is read from `XAI_API_KEY` or the ignored local `xai_api_key.txt`
file. It is not saved in ComfyUI workflow files.
