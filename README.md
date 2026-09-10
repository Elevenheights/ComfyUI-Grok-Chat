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

## Add the xAI key on RunPod

Use a RunPod Secret so the API key is not stored in a workflow, shell history, or public template:

1. Open the RunPod console and go to **Secrets**.
2. Create a secret named `xai_api_key` and paste the xAI API key as its value.
3. Open **Pods**, click the three-dot menu beside the ComfyUI pod, and choose **Edit Pod**.
4. Expand **Environment Variables** and add:
   - **Key:** `XAI_API_KEY`
   - **Value:** `{{ RUNPOD_SECRET_xai_api_key }}`
5. Save the pod. RunPod restarts it to apply the environment variable.

Pod edits can clear files outside the mounted volume. Keep ComfyUI and its custom nodes under `/workspace`.

After the pod restarts, verify that the variable exists without displaying the secret:

```bash
python -c "import os; print('XAI_API_KEY configured:', bool(os.getenv('XAI_API_KEY')))"
```

The output should be `XAI_API_KEY configured: True`. Restart ComfyUI once more if the application process was already running before the variable was added.

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
