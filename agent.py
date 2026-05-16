import json
import os
from groq import Groq
from tools import TOOLS, TOOL_MAP
from dotenv import load_dotenv

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"

MAX_ITERATIONS = 10

SYSTEM_PROMPT = """You are Snow, an autonomous AI agent — powerful, precise, and proactive.

You have access to these tools:
- web_search: search the internet for any information
- scrape_webpage: read full content of any webpage
- run_python: execute Python code for calculations, data processing, automation
- run_shell: run system commands
- read_file / write_file / list_files: work with the filesystem

## How you work:
1. Analyze the user's task carefully
2. Break it into steps
3. Use tools to complete each step — don't guess, look things up
4. Loop until the task is fully done
5. Give a clear, well-formatted final answer

## Rules:
- Always use tools when you need real information — never make things up
- After web_search, use scrape_webpage on the best result to get full details
- When writing reports or files, write them properly and confirm the file was saved
- Be thorough but efficient — don't use more tool calls than needed
- Format your final answer clearly with headers, bullets, and structure

You are capable of completing complex multi-step tasks autonomously. Be confident and thorough."""


def run_agent(task: str, on_step=None) -> str:
    """
    Run the agent on a task.
    on_step: optional callback(step_type, content) for streaming steps to UI
    Returns the final answer string.
    """
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]

    if on_step:
        on_step("task", f"Task received: {task}")

    for iteration in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=4096,
            temperature=0.3,
        )

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # No more tool calls — agent is done
        if finish_reason == "stop" or not msg.tool_calls:
            final = msg.content or "Task completed."
            if on_step:
                on_step("final", final)
            return final

        # Process tool calls
        messages.append({
            "role": "assistant",
            "content": msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in msg.tool_calls
            ]
        })

        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            if on_step:
                on_step("tool_call", f"Calling **{tool_name}** with: `{json.dumps(args, ensure_ascii=False)[:200]}`")

            # Execute the tool
            if tool_name in TOOL_MAP:
                result = TOOL_MAP[tool_name](**args)
            else:
                result = f"Unknown tool: {tool_name}"

            if on_step:
                preview = str(result)[:300] + ("..." if len(str(result)) > 300 else "")
                on_step("tool_result", f"Result from **{tool_name}**:\n```\n{preview}\n```")

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

    return "Snow reached maximum iterations. Task may be incomplete."


if __name__ == "__main__":
    print("Snow — Autonomous AI Agent — type 'quit' to exit\n")
    while True:
        task = input("You: ").strip()
        if task.lower() in ("quit", "exit"):
            break
        if not task:
            continue

        def print_step(step_type, content):
            icons = {"task": "📋", "tool_call": "🔧", "tool_result": "📊", "final": "✅"}
            print(f"\n{icons.get(step_type, '•')} {content}")

        result = run_agent(task, on_step=print_step)
        print(f"\n{'='*60}\nFinal Answer:\n{result}\n{'='*60}\n")