import subprocess
import os
import sys
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import tempfile
import json

# ── Web search ────────────────────────────────────────────────────────────────

def web_search(query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return formatted results."""
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"Title: {r['title']}\nURL: {r['href']}\nSnippet: {r['body']}\n")
        if not results:
            return "No results found."
        return "\n---\n".join(results)
    except Exception as e:
        return f"Search error: {e}"


# ── Web scrape ────────────────────────────────────────────────────────────────

def scrape_webpage(url: str, max_chars: int = 4000) -> str:
    """Fetch and extract clean text from a webpage."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        return text[:max_chars] + ("..." if len(text) > max_chars else "")
    except Exception as e:
        return f"Scrape error: {e}"


# ── Python execution ──────────────────────────────────────────────────────────

def run_python(code: str) -> str:
    """Execute Python code and return stdout + stderr."""
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            tmp_path = f.name
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True, text=True, timeout=30
        )
        os.unlink(tmp_path)
        output = ""
        if result.stdout:
            output += f"Output:\n{result.stdout}"
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
        return output.strip() or "Code ran with no output."
    except subprocess.TimeoutExpired:
        return "Code execution timed out (30s limit)."
    except Exception as e:
        return f"Execution error: {e}"


# ── Shell commands ────────────────────────────────────────────────────────────

def run_shell(command: str) -> str:
    """Run a shell command and return output. Blocked dangerous commands."""
    blocked = ["rm -rf", "format", "del /f", "shutdown", "reboot", ":(){", "dd if"]
    for b in blocked:
        if b in command.lower():
            return f"Blocked: '{b}' is not allowed for safety."
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True,
            text=True, timeout=15
        )
        output = result.stdout + result.stderr
        return output.strip() or "Command ran with no output."
    except subprocess.TimeoutExpired:
        return "Command timed out (15s limit)."
    except Exception as e:
        return f"Shell error: {e}"


# ── File operations ───────────────────────────────────────────────────────────

def read_file(path: str) -> str:
    """Read contents of a file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:5000] + ("..." if len(content) > 5000 else "")
    except Exception as e:
        return f"Read error: {e}"


def write_file(path: str, content: str) -> str:
    """Write content to a file."""
    try:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Successfully wrote {len(content)} characters to {path}"
    except Exception as e:
        return f"Write error: {e}"


def list_files(directory: str = ".") -> str:
    """List files in a directory."""
    try:
        items = os.listdir(directory)
        files = [f"{'[DIR] ' if os.path.isdir(os.path.join(directory, f)) else ''}{f}" for f in items]
        return "\n".join(files) or "Empty directory."
    except Exception as e:
        return f"List error: {e}"


# ── Tool registry ─────────────────────────────────────────────────────────────

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for current information, news, facts, or any topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {"type": "integer", "description": "Number of results to return"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_webpage",
            "description": "Fetch and read the full content of a webpage given its URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The URL to scrape"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python",
            "description": "Execute Python code and return the output. Use for calculations, data processing, or any computation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "Run a shell command on the system.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"}
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file from the filesystem.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file. Creates directories if needed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write to"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories in a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path (default: current directory)"}
                }
            }
        }
    }
]

TOOL_MAP = {
    "web_search": web_search,
    "scrape_webpage": scrape_webpage,
    "run_python": run_python,
    "run_shell": run_shell,
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
}
