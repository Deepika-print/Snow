import json
import os
import re
from groq import Groq
from tools import TOOLS, TOOL_MAP
from dotenv import load_dotenv

load_dotenv()

# Use only models that reliably support tool calling
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_ITERATIONS = 8
MAX_TASK_LENGTH = 2000

BLOCKED_PATTERNS = [
    r"ignore (previous|all) instructions",
    r"you are now", r"pretend you are",
    r"jailbreak", r"dan mode",
]

SYSTEM_PROMPT = """You are Snow, a helpful and precise AI assistant.

You have access to tools. Use them to answer questions accurately.

IMPORTANT: Always give a complete, detailed final answer. Never say just "task completed" - actually answer the question with the information you found.

For any factual question, use web_search to find the answer, then provide a comprehensive response."""


def validate_task(task):
    if not task or not task.strip():
        return False, "Task cannot be empty."
    if len(task) > MAX_TASK_LENGTH:
        return False, f"Task too long. Max {MAX_TASK_LENGTH} characters."
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, task.lower()):
            return False, "Task contains disallowed content."
    return True, ""


def run_agent(task: str, on_step=None) -> str:
    is_safe, reason = validate_task(task)
    if not is_safe:
        return f"❌ {reason}"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": task}
    ]

    if on_step:
        on_step("task", task)

    for iteration in range(MAX_ITERATIONS):
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                max_tokens=2048,
                temperature=0.1,
            )
        except Exception as e:
            error_str = str(e)
            # Tool calling failed — answer directly without tools
            if "tool_use_failed" in error_str or "Failed to call" in error_str:
                if on_step:
                    on_step("info", "Answering directly without tools")
                try:
                    direct = client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=messages,
                        max_tokens=2048,
                        temperature=0.3,
                    )
                    answer = direct.choices[0].message.content or "I couldn't complete this task."
                    if on_step:
                        on_step("final", answer)
                    return answer
                except Exception as e2:
                    error_msg = f"Error: {str(e2)}"
                    if on_step:
                        on_step("final", error_msg)
                    return error_msg
            error_msg = f"Error: {error_str}"
            if on_step:
                on_step("final", error_msg)
            return error_msg

        msg = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # No tool calls — this is the final answer
        if finish_reason == "stop" or not msg.tool_calls:
            final = msg.content or "I completed the task."
            if on_step:
                on_step("final", final)
            return final

        # Add assistant message
        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{
                "id": tc.id,
                "type": "function",
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in msg.tool_calls]
        })

        # Execute tools
        for tc in msg.tool_calls:
            tool_name = tc.function.name
            try:
                args = json.loads(tc.function.arguments)
            except Exception:
                args = {}

            if on_step:
                on_step("tool_call", f"Using {tool_name}: {json.dumps(args)[:150]}")

            if tool_name in TOOL_MAP:
                try:
                    result = TOOL_MAP[tool_name](**args)
                except Exception as e:
                    result = f"Tool error: {e}"
            else:
                result = f"Unknown tool: {tool_name}"

            if on_step:
                on_step("tool_result", str(result)[:300])

            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": str(result)
            })

    # Max iterations reached — get final answer from current context
    try:
        final_resp = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages + [{"role": "user", "content": "Please provide your final comprehensive answer now."}],
            max_tokens=2048,
            temperature=0.3,
        )
        final = final_resp.choices[0].message.content or "Task completed."
        if on_step:
            on_step("final", final)
        return final
    except Exception:
        return "Snow reached maximum iterations. Please try a simpler task."


if __name__ == "__main__":
    print("❄️ Snow — type 'quit' to exit\n")
    while True:
        task = input("You: ").strip()
        if task.lower() in ("quit", "exit", "q"):
            break
        if not task:
            continue
        result = run_agent(task, on_step=lambda t, c: print(f"[{t}] {c[:200]}"))
        print(f"\n❄️ {result}\n{'─'*50}\n")
        
    else:
        print("Goodbye!")
