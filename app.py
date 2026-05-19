import gradio as gr
import os
import threading
import time
from agent import run_agent
from dotenv import load_dotenv

load_dotenv()

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;500;600;700;800&display=swap');
* { box-sizing: border-box; }
body, .gradio-container { background: #0a0a0f !important; font-family: 'Syne', sans-serif !important; }
.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }
#steps-log textarea { font-family: 'Space Mono', monospace !important; font-size: 11px !important; background: #080d14 !important; color: #6b8099 !important; border: 1px solid #0e1e2e !important; }
#task-input textarea { background: #080d14 !important; border: 1px solid #0e1e2e !important; color: #e0eaf5 !important; font-family: 'Syne', sans-serif !important; font-size: 14px !important; }
#send-btn { background: #004c6e !important; color: white !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; border: none !important; }
#send-btn:hover { background: #006a9a !important; }
"""


def respond(message, history):
    if not message.strip():
        return history, "", "Waiting for task...\n"

    if not os.getenv("GROQ_API_KEY"):
        history = history + [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "⚠️ GROQ_API_KEY not set. Add it to your .env file or Hugging Face Secrets."}
        ]
        return history, "", "Error: No API key\n"

    steps_log = f"{'─'*40}\n◆ TASK: {message[:80]}\n"
    result_holder = {"final": None, "done": False}
    step_buffer = []

    def on_step(step_type, content):
        step_buffer.append((step_type, content))

    def agent_thread():
        try:
            result_holder["final"] = run_agent(message, on_step=on_step)
        except Exception as e:
            result_holder["final"] = f"Error: {e}"
        result_holder["done"] = True

    t = threading.Thread(target=agent_thread, daemon=True)
    t.start()

    timeout = 120
    elapsed = 0
    while not result_holder["done"] and elapsed < timeout:
        time.sleep(0.5)
        elapsed += 0.5
        while step_buffer:
            stype, scontent = step_buffer.pop(0)
            icons = {"task": "◆", "tool_call": "⚙", "tool_result": "◎", "final": "✓", "info": "ℹ"}
            steps_log += f"{icons.get(stype,'•')} {scontent[:120]}\n"

    t.join(timeout=5)

    while step_buffer:
        stype, scontent = step_buffer.pop(0)
        icons = {"task": "◆", "tool_call": "⚙", "tool_result": "◎", "final": "✓", "info": "ℹ"}
        steps_log += f"{icons.get(stype,'•')} {scontent[:120]}\n"

    final = result_holder["final"]
    if not final:
        final = "Snow timed out. Please try again with a simpler task."

    steps_log += f"✓ DONE\n{'─'*40}\n"
    history = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": final}
    ]
    return history, "", steps_log


with gr.Blocks(title="Snow — Autonomous AI Agent") as demo:

    gr.HTML("""
    <div style="text-align:center;padding:32px 24px 20px;">
      <h1 style="font-family:'Syne',sans-serif;font-size:42px;font-weight:800;color:#fff;letter-spacing:-2px;margin:0;">
        SNO<span style="color:#004c6e">W</span>
      </h1>
      <p style="font-family:'Space Mono',monospace;font-size:11px;color:#6b8099;letter-spacing:3px;margin-top:8px;">
        AUTONOMOUS AI · GROQ · LLAMA 3.1 70B
      </p>
    </div>
    <div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin:0 24px 24px;">
      <span style="font-family:'Space Mono',monospace;font-size:10px;padding:3px 12px;border-radius:20px;border:1px solid #004c6e33;color:#004c6e;background:#004c6e0a;">Web Search</span>
      <span style="font-family:'Space Mono',monospace;font-size:10px;padding:3px 12px;border-radius:20px;border:1px solid #004c6e33;color:#004c6e;background:#004c6e0a;">Web Scrape</span>
      <span style="font-family:'Space Mono',monospace;font-size:10px;padding:3px 12px;border-radius:20px;border:1px solid #004c6e33;color:#004c6e;background:#004c6e0a;">Run Python</span>
      <span style="font-family:'Space Mono',monospace;font-size:10px;padding:3px 12px;border-radius:20px;border:1px solid #004c6e33;color:#004c6e;background:#004c6e0a;">Shell</span>
      <span style="font-family:'Space Mono',monospace;font-size:10px;padding:3px 12px;border-radius:20px;border:1px solid #004c6e33;color:#004c6e;background:#004c6e0a;">File I/O</span>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(
                label="CONVERSATION",
                height=420,
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

        with gr.Column(scale=1):
            steps_log = gr.Textbox(
                label="AGENT STEPS",
                value="Waiting for task...\n",
                lines=20,
                max_lines=20,
                interactive=False,
                elem_id="steps-log",
            )

    gr.HTML("""
    <div style="padding:0 24px 24px;">
      <p style="font-family:'Space Mono',monospace;font-size:10px;color:#444455;letter-spacing:2px;margin-bottom:10px;">TRY THESE</p>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px;">
        <div style="padding:10px 14px;border-radius:10px;border:1px solid #0e1e2e;background:#080d14;color:#6b8099;font-family:Syne,sans-serif;font-size:12px;cursor:pointer;">Search for latest AI news today</div>
        <div style="padding:10px 14px;border-radius:10px;border:1px solid #0e1e2e;background:#080d14;color:#6b8099;font-family:Syne,sans-serif;font-size:12px;cursor:pointer;">Write and run a Python Fibonacci script</div>
        <div style="padding:10px 14px;border-radius:10px;border:1px solid #0e1e2e;background:#080d14;color:#6b8099;font-family:Syne,sans-serif;font-size:12px;cursor:pointer;">Who is PM of India? Search it</div>
        <div style="padding:10px 14px;border-radius:10px;border:1px solid #0e1e2e;background:#080d14;color:#6b8099;font-family:Syne,sans-serif;font-size:12px;cursor:pointer;">Top 5 free AI tools in 2026</div>
      </div>
    </div>
    """)

    send_btn.click(
        fn=respond,
        inputs=[task_input, chatbot],
        outputs=[chatbot, task_input, steps_log],
    )
    task_input.submit(
        fn=respond,
        inputs=[task_input, chatbot],
        outputs=[chatbot, task_input, steps_log],
    )

demo.launch(css=CSS)
