import gradio as gr
import os
import threading
from agent import run_agent
from dotenv import load_dotenv

load_dotenv()

# ── CSS — dark terminal aesthetic ─────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

* { box-sizing: border-box; }

body, .gradio-container {
    background: #0a0a0f !important;
    font-family: 'Syne', sans-serif !important;
}

.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: 0 !important;
}

/* Header */
.agent-header {
    text-align: center;
    padding: 48px 24px 32px;
    position: relative;
}

.agent-header::before {
    content: '';
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 1px; height: 48px;
    background: linear-gradient(to bottom, transparent, #00ff9d);
}

.agent-title {
    font-family: 'Syne', sans-serif;
    font-size: 48px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -2px;
    margin: 0;
    line-height: 1;
}

.agent-title span {
    color: #00ff9d;
}

.agent-sub {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #555566;
    margin-top: 12px;
    letter-spacing: 3px;
    text-transform: uppercase;
}

/* Tool badges */
.tools-row {
    display: flex;
    justify-content: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 0 24px 32px;
}

.tool-badge {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    padding: 4px 12px;
    border-radius: 20px;
    border: 1px solid #1a1a2e;
    color: #555566;
    background: #0d0d18;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.tool-badge.active { border-color: #00ff9d33; color: #00ff9d; background: #00ff9d0a; }

/* Main layout */
.main-layout {
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 16px;
    padding: 0 24px 24px;
}

@media (max-width: 768px) { .main-layout { grid-template-columns: 1fr; } }

/* Chat area */
.chat-panel {
    background: #0d0d18;
    border: 1px solid #1a1a2e;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}

.chat-header {
    padding: 16px 20px;
    border-bottom: 1px solid #1a1a2e;
    display: flex;
    align-items: center;
    gap: 8px;
}

.dot { width: 8px; height: 8px; border-radius: 50%; }
.dot-red { background: #ff5f56; }
.dot-yellow { background: #ffbd2e; }
.dot-green { background: #27c93f; }

.chat-title {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #555566;
    margin-left: 4px;
    letter-spacing: 1px;
}

/* Chatbot messages */
#chatbot {
    background: transparent !important;
    flex: 1;
}

#chatbot .message {
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    line-height: 1.7 !important;
}

#chatbot .user { 
    background: #1a1a2e !important; 
    border: 1px solid #2a2a3e !important;
    border-radius: 12px 12px 4px 12px !important;
    color: #e0e0f0 !important;
}

#chatbot .bot { 
    background: #0a0a14 !important; 
    border: 1px solid #1a1a2e !important;
    border-radius: 12px 12px 12px 4px !important;
    color: #c0c0d0 !important;
}

/* Input area */
.input-area {
    padding: 16px;
    border-top: 1px solid #1a1a2e;
    display: flex;
    gap: 8px;
    align-items: flex-end;
}

#task-input textarea {
    background: #050510 !important;
    border: 1px solid #1a1a2e !important;
    border-radius: 10px !important;
    color: #e0e0f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 14px !important;
    resize: none !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s !important;
}

#task-input textarea:focus {
    border-color: #00ff9d55 !important;
    outline: none !important;
    box-shadow: 0 0 0 3px #00ff9d0a !important;
}

#task-input textarea::placeholder { color: #333344 !important; }

#send-btn {
    background: #00ff9d !important;
    color: #000000 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 12px 24px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    white-space: nowrap !important;
    letter-spacing: 0.5px !important;
}

#send-btn:hover { background: #00cc7a !important; transform: translateY(-1px) !important; }
#send-btn:active { transform: translateY(0) !important; }

/* Steps panel */
.steps-panel {
    background: #0d0d18;
    border: 1px solid #1a1a2e;
    border-radius: 16px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    max-height: 600px;
}

.steps-header {
    padding: 16px 20px;
    border-bottom: 1px solid #1a1a2e;
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: #555566;
    letter-spacing: 1px;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #333344;
    transition: background 0.3s;
}

.status-dot.active { background: #00ff9d; box-shadow: 0 0 8px #00ff9d; }

#steps-log {
    background: transparent !important;
    border: none !important;
    flex: 1;
    font-family: 'Space Mono', monospace !important;
    font-size: 11px !important;
    color: #555566 !important;
    line-height: 1.8 !important;
    overflow-y: auto !important;
    padding: 16px !important;
}

/* Stats */
.stats-row {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1px;
    border-top: 1px solid #1a1a2e;
}

.stat {
    padding: 12px;
    text-align: center;
    background: #0a0a14;
}

.stat-val {
    font-family: 'Space Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #00ff9d;
}

.stat-lbl {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: #333344;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-top: 2px;
}

/* Clear button */
#clear-btn {
    background: transparent !important;
    border: 1px solid #1a1a2e !important;
    color: #555566 !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 10px !important;
    padding: 6px 14px !important;
    cursor: pointer !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}

#clear-btn:hover { border-color: #ff5f5655 !important; color: #ff5f56 !important; }

/* Example tasks */
.examples-section {
    padding: 0 24px 24px;
}

.examples-title {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    color: #333344;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 8px;
}
"""

# ── State ─────────────────────────────────────────────────────────────────────
_stats = {"tasks": 0, "tools": 0, "steps": 0}


def format_step(step_type: str, content: str) -> str:
    icons = {
        "task":        "◆ TASK",
        "tool_call":   "⚙ TOOL",
        "tool_result": "◎ RESULT",
        "final":       "✓ DONE",
    }
    label = icons.get(step_type, "• INFO")
    lines = content.split("\n")
    first = lines[0][:120]
    return f"[{label}] {first}\n"


def run_task(task: str, history, steps_log: str):
    if not task.strip():
        yield history, steps_log, "0", "0", "0", ""
        return

    if not os.getenv("GROQ_API_KEY"):
        history = history or []
        history.append({"role": "user", "content": task})
        history.append({"role": "assistant", "content": "⚠️ GROQ_API_KEY not set. Add it to your .env file."})
        yield history, steps_log, str(_stats["tasks"]), str(_stats["tools"]), str(_stats["steps"]), ""
        return

    _stats["tasks"] += 1
    history = history or []
    history = history + [{"role":"user","content":task},{"role":"assistant","content":"⟳ Snow is working..."}]

    steps_log = f"{'─'*40}\n"
    step_buffer = []
    result_holder = {"final": None}

    def on_step(step_type, content):
        step_buffer.append((step_type, content))
        if step_type == "tool_call":
            _stats["tools"] += 1
        _stats["steps"] += 1

    def agent_thread():
        result_holder["final"] = run_agent(task, on_step=on_step)

    t = threading.Thread(target=agent_thread)
    t.start()

    import time
    while t.is_alive() or step_buffer:
        while step_buffer:
            stype, scontent = step_buffer.pop(0)
            steps_log += format_step(stype, scontent)
            yield history, steps_log, str(_stats["tasks"]), str(_stats["tools"]), str(_stats["steps"]), ""
        time.sleep(0.2)

    t.join()

    if result_holder["final"]:
        history[-1] = {"role":"assistant","content":result_holder["final"]}
    else:
        history[-1] = {"role":"assistant","content":"Snow completed the task."}

    steps_log += format_step("final", "Agent finished.")
    yield history, steps_log, str(_stats["tasks"]), str(_stats["tools"]), str(_stats["steps"]), ""


# ── UI ────────────────────────────────────────────────────────────────────────
EXAMPLES = [
    "Search for the latest AI news today and write a summary report",
    "Write a Python script to generate a Fibonacci sequence and run it",
    "Search for the best Python learning resources and save them to a file",
    "What is the current weather in Delhi? Search and summarize",
]

with gr.Blocks(title="Snow — Autonomous AI Agent") as demo:

    # Header
    gr.HTML("""
    <div class="agent-header">
        <h1 class="agent-title">SNO<span>W</span></h1>
        <p class="agent-sub">Autonomous AI · Powered by Groq · LLaMA 3.3 70B</p>
    </div>
    <div class="tools-row">
        <span class="tool-badge active">Web Search</span>
        <span class="tool-badge active">Web Scrape</span>
        <span class="tool-badge active">Run Python</span>
        <span class="tool-badge active">Shell</span>
        <span class="tool-badge active">File I/O</span>
        <span class="tool-badge">Memory</span>
    </div>
    """)

    with gr.Row(elem_classes=["main-layout"]):

        # Left — chat
        with gr.Column():
            gr.HTML("""
            <div class="chat-panel" style="border-radius:16px;overflow:hidden">
              <div class="chat-header">
                <div class="dot dot-red"></div>
                <div class="dot dot-yellow"></div>
                <div class="dot dot-green"></div>
                <span class="chat-title">CONVERSATION</span>
              </div>
            </div>
            """)
            chatbot = gr.Chatbot(
                label="",
                height=400,
                show_label=False,
                elem_id="chatbot",
            )
            with gr.Row():
                task_input = gr.Textbox(
                    placeholder="Give Snow a task — I'll search, code, and execute autonomously...",
                    label="",
                    lines=2,
                    elem_id="task-input",
                    scale=5,
                )
                send_btn = gr.Button("RUN →", elem_id="send-btn", scale=1)

        # Right — steps + stats
        with gr.Column():
            gr.HTML("""
            <div class="steps-panel" style="border-radius:16px">
              <div class="steps-header">
                <span>AGENT STEPS</span>
                <div class="status-dot" id="sdot"></div>
              </div>
            </div>
            """)
            steps_log = gr.Textbox(
                value="Snow is ready...\n",
                label="",
                lines=18,
                max_lines=18,
                show_label=False,
                elem_id="steps-log",
                interactive=False,
            )
            gr.HTML("""<div class="stats-row">
              <div class="stat"><div class="stat-val" id="sv-tasks">0</div><div class="stat-lbl">Tasks</div></div>
              <div class="stat"><div class="stat-val" id="sv-tools">0</div><div class="stat-lbl">Tool Calls</div></div>
              <div class="stat"><div class="stat-val" id="sv-steps">0</div><div class="stat-lbl">Steps</div></div>
            </div>""")
            with gr.Row():
                tasks_out = gr.Textbox(visible=False)
                tools_out = gr.Textbox(visible=False)
                steps_out = gr.Textbox(visible=False)
            clear_btn = gr.Button("CLEAR", elem_id="clear-btn")

    # Examples
    gr.HTML('<div class="examples-section"><div class="examples-title">Try these</div><div class="examples-grid">')
    with gr.Row():
        for ex in EXAMPLES:
            gr.Button(ex[:60] + ("..." if len(ex) > 60 else ""), size="sm").click(
                fn=lambda e=ex: e, outputs=[task_input]
            )
    gr.HTML('</div></div>')

    # Wire up
    send_btn.click(
        fn=run_task,
        inputs=[task_input, chatbot, steps_log],
        outputs=[chatbot, steps_log, tasks_out, tools_out, steps_out, task_input],
    )
    task_input.submit(
        fn=run_task,
        inputs=[task_input, chatbot, steps_log],
        outputs=[chatbot, steps_log, tasks_out, tools_out, steps_out, task_input],
    )
    clear_btn.click(
        fn=lambda: ([], "Snow is ready...\n", "", "", ""),
        outputs=[chatbot, steps_log, tasks_out, tools_out, steps_out, task_input],
    )


if __name__ == "__main__":
    demo.launch(server_port=7864, inbrowser=True, css=CSS, share= True)