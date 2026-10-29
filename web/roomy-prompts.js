import { app } from "../../scripts/app.js";

const fields = [
  ["prompt", "Prompt", 360],
  ["additional_text", "Additional text", 220],
  ["system_instruction", "System instructions", 180],
];

function largeEditor(node) {
  node.grokCloseEditor?.();
  const dialog = document.createElement("dialog");
  dialog.className = "grok-prompt-editor";
  dialog.setAttribute("aria-label", "Grok prompt editor");
  const previous = document.activeElement;
  const header = document.createElement("header");
  const title = document.createElement("strong");
  title.textContent = "Grok / OpenAI · Prompt editor";
  const close = document.createElement("button");
  close.textContent = "Done";
  close.type = "button";
  close.onclick = () => dialog.close();
  header.append(title, close);
  dialog.append(header);
  const body = document.createElement("div");
  body.className = "grok-editor-fields";
  for (const [name, label, height] of fields) {
    const widget = node.widgets?.find(w => w.name === name);
    if (!widget) continue;
    const section = document.createElement("label");
    const caption = document.createElement("span");
    caption.textContent = label;
    const input = document.createElement("textarea");
    input.value = widget.value ?? "";
    input.style.height = `${height}px`;
    input.setAttribute("aria-label", label);
    input.spellcheck = false;
    input.addEventListener("input", () => {
      widget.value = input.value;
      widget.callback?.(input.value);
      app.graph?.setDirtyCanvas(true, true);
    });
    section.append(caption, input);
    body.append(section);
  }
  dialog.append(body);
  dialog.addEventListener("close", () => {
    dialog.remove();
    node.grokCloseEditor = null;
    previous?.focus?.();
  }, {once: true});
  document.body.append(dialog);
  node.grokCloseEditor = () => dialog.close();
  dialog.showModal();
  body.querySelector("textarea")?.focus();
}

function applyHeights(node) {
  const scale = node.properties.grokTextScale ?? 1;
  for (const [name, , baseHeight] of fields) {
    const widget = node.widgets?.find(w => w.name === name);
    if (!widget) continue;
    const height = Math.round(baseHeight * scale);
    widget.options ??= {};
    widget.options.getMinHeight = () => height;
    widget.options.getHeight = () => height;
    widget.options.getMaxHeight = () => height;
    widget.computeSize = width => [width, height];
    const element = widget.inputEl ?? widget.element;
    if (element) {
      element.style.setProperty("--comfy-widget-min-height", `${height}px`);
      element.style.setProperty("--comfy-widget-height", `${height}px`);
      element.style.fontSize = "14px";
      element.style.lineHeight = "1.5";
    }
  }
  const size = node.computeSize();
  node.setSize([Math.max(720, node.size[0]), Math.max(size[1], 1000 * scale)]);
  app.graph?.setDirtyCanvas(true, true);
}

app.registerExtension({
  name: "GrokChat.RoomyPrompts",
  async setup() {
    const style = document.createElement("style");
    style.textContent = `
      .grok-prompt-editor{width:88vw;height:86vh;max-width:96vw;max-height:96vh;min-width:min(420px,90vw);min-height:360px;resize:both;overflow:hidden;padding:0;border:1px solid #78618f;border-radius:12px;background:#211b2a;color:#eee;font:14px system-ui}
      .grok-prompt-editor::backdrop{background:#000b}
      .grok-prompt-editor header{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:16px;border-bottom:1px solid #574563;height:64px}
      .grok-prompt-editor button{padding:8px 20px;background:#754aa5;color:white;border:1px solid #a581ca;border-radius:6px;cursor:pointer}
      .grok-editor-fields{height:calc(100% - 64px);overflow:auto;padding:18px;box-sizing:border-box}
      .grok-editor-fields label{display:block;margin-bottom:20px}
      .grok-editor-fields span{display:block;font-weight:600;margin-bottom:8px}
      .grok-editor-fields textarea{display:block;box-sizing:border-box;width:100%;min-height:120px;max-width:100%;resize:vertical;overflow:auto;background:#14111a;color:#f0eaf7;border:1px solid #756383;border-radius:7px;padding:14px;font:15px/1.6 system-ui;white-space:pre-wrap}
      .grok-editor-fields textarea:focus{outline:2px solid #b68ee1;outline-offset:1px}
    `;
    document.head.append(style);
  },
  async beforeRegisterNodeDef(nodeType, data) {
    if (data.name !== "GrokChatNode") return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const result = created?.apply(this, arguments);
      this.properties ??= {};
      this.addWidget("button", "Open large prompt editor", null, () => largeEditor(this), {serialize: false});
      for (const [label, delta] of [["Make text boxes taller", 0.25], ["Make text boxes shorter", -0.25]]) {
        this.addWidget("button", label, null, () => {
          this.properties.grokTextScale = Math.max(0.5, Math.min(3, (this.properties.grokTextScale ?? 1) + delta));
          applyHeights(this);
        }, {serialize: false});
      }
      applyHeights(this);
      return result;
    };
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const result = configured?.apply(this, arguments);
      applyHeights(this);
      return result;
    };
    const removed = nodeType.prototype.onRemoved;
    nodeType.prototype.onRemoved = function () {
      this.grokCloseEditor?.();
      return removed?.apply(this, arguments);
    };
  },
});
