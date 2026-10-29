# ComfyUI Grok Chat

A ComfyUI custom node for sending text and optional image inputs to xAI Grok models. It supports system instructions, additional prompt text, conversation context, model selection, temperature, top-p, and seed controls.

## Larger prompt editor

Prompt, Additional Text and System Instructions now have larger fields in the
node. Use **Make text boxes taller** or **Make text boxes shorter** to adjust
all three. The size setting is saved with the workflow.

Choose **Open large prompt editor** for a roomy editing window. Drag the window's
bottom-right corner to resize it, or drag the bottom-right corner of an individual
text box to change its height. Text changes apply directly to the node; **Done**
or Escape closes the editor. The editor uses the same prompts and API settings
as the node.

To update an installation cloned with Git, run `git pull` inside the node folder,
then restart ComfyUI and refresh the browser. For ZIP installations, replace the
node files with the latest download while keeping your API key files. Include
the new `web` folder when installing or updating.

## Install and setup

### 1. Install the node

For a standard installation, open a terminal in the folder containing ComfyUI's
`main.py` and activate the same Python environment used to start ComfyUI:

```bash
git clone https://github.com/Elevenheights/ComfyUI-Grok-Chat.git custom_nodes/comfyui_grok_chat
python -m pip install -r custom_nodes/comfyui_grok_chat/requirements.txt
```

For **Windows Portable**, run from the outer folder containing `ComfyUI` and
`python_embeded`:

```powershell
git clone https://github.com/Elevenheights/ComfyUI-Grok-Chat.git .\ComfyUI\custom_nodes\comfyui_grok_chat
.\python_embeded\python.exe -m pip install -r .\ComfyUI\custom_nodes\comfyui_grok_chat\requirements.txt
```

Without Git, choose **Code > Download ZIP** on GitHub, extract it into
`ComfyUI/custom_nodes`, and rename the folder to `comfyui_grok_chat`.
`__init__.py` must be directly inside that folder. Install its requirements using
the appropriate command above.

### 2. Create your xAI API key

Create an account at [console.x.ai](https://console.x.ai), configure API billing
or credits, then create an API key in **API Keys**. Follow the
[official quickstart](https://docs.x.ai/developers/quickstart) for account setup.
Reference captioning sends the supplied image and prompt to xAI and uses your
API account's usage allowance/billing.

Create a plain-text file named **`xai_api_key.txt`** inside the installed
`comfyui_grok_chat` folder and paste only your key into it. Ensure the filename
does not become `xai_api_key.txt.txt` on Windows.

For Windows Portable, you can open it from the outer portable folder:

```powershell
notepad .\ComfyUI\custom_nodes\comfyui_grok_chat\xai_api_key.txt
```

For standard Windows installations, open
`custom_nodes/comfyui_grok_chat/xai_api_key.txt` under your ComfyUI folder.

On the common RunPod template, use the pod terminal:

```bash
nano /workspace/ComfyUI/custom_nodes/comfyui_grok_chat/xai_api_key.txt
```

Paste only your key, then press `Ctrl+O`, `Enter`, and `Ctrl+X`. Keep ComfyUI on
your persistent volume; the usual template path is `/workspace/ComfyUI`, but
verify your template's actual storage mount. Restart ComfyUI after saving the key
so the model list reloads, then refresh the browser.

If the repository was cloned using a different folder name, edit
`xai_api_key.txt` inside that folder instead. Advanced installations may still
use the `XAI_API_KEY` environment variable; it takes priority over the file.
Set it in the ComfyUI server's environment before launch. This node does not
automatically read a `.env` file. The key file is ignored by Git and the API key
is not saved in workflow JSON.

### 3. Configure FAMEGRID ULTRAREAL

- **Reference to Image:** select the local reference folder in the image loader.
  Grok describes the reference, then the first pass generates from an empty
  latent canvas at denoise **1.00**.
- **Image to Image:** select the local reference folder. The image supplies both
  the Grok caption and the encoded starting latent; first-pass denoise is **0.72**.
- **True Text to Image:** write directly into the positive prompt box. This
  edition has no Grok or reference-image nodes and does not need an xAI key.

In the Grok node, select an available **Grok model with image-understanding
support** from your account's model list. If your installed node exposes a
`provider` field, use **grok**, or **auto** with a Grok model selected. Edit the
character opener/description to match your subject, and set **keep_context =
false** for independent image captions. Use the first-pass route panel to choose
**Fast Mode (KSampler)** or **Quality (slower, ClownShark)**; this does not change
the caption provider.

If a workflow's saved model is no longer available, choose an available
image-understanding model after configuring the key and restarting ComfyUI.

Photo finishing uses the separate
[FameGrid Photo Pro package](https://github.com/Elevenheights/ComfyUI-FameGridPhotoPro#install),
or the companion Camera Raw workflow edition.

## Updates and troubleshooting

From the ComfyUI folder, with its Python environment active:

```bash
git -C custom_nodes/comfyui_grok_chat pull --ff-only
python -m pip install -r custom_nodes/comfyui_grok_chat/requirements.txt
```

Portable users should use the embedded Python and prepend `ComfyUI/` to these
paths when running from the outer portable folder. Restart ComfyUI and refresh
the browser after updating; wait for active jobs to finish first.

- **Node missing/import failure:** check the ComfyUI terminal and install the
  requirements using ComfyUI's Python.
- **Missing key / HTTP 401:** check the key file's location and filename, or the
  server's `XAI_API_KEY`. An old environment key overrides the file.
- **Model unavailable or image rejected:** select a model available to your API
  account that supports image inputs; restart after changing credentials.
- **Quota or rate-limit error:** check API billing/credits and account limits in
  the xAI console.
- **Wrong reference on RunPod:** a local PC's folder path is not available on the
  pod. Upload the reference images and select a folder on the ComfyUI server.

Join our [Discord](https://discord.gg/hXmy4zVsEq) for support, updates and early access.

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
