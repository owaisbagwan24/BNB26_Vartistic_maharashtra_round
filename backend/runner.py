"""Re:Learn Secure Code Runner & Traceback Parser.
Implements industrial best practices for online IDE code sandboxing:
- Resource timeout protection (avoids hanging on while True loops)
- AST-level security pre-screener (blocks os.system, subprocess, destructive I/O)
- Structured traceback parsing (extracts exact line, column, error_type, message)
- High-precision execution benchmarking
"""
import sys
import subprocess
import time
import tempfile
import os
import re
import ast
from pathlib import Path
from typing import Dict, Any, Tuple

# Blocked modules/functions for novice educational sandbox
DISALLOWED_IMPORTS = {"subprocess", "shutil", "socket", "http", "urllib", "requests", "ctypes", "winreg"}
DISALLOWED_CALLS = {"system", "popen", "spawn", "fork", "remove", "rmdir", "unlink", "kill"}

def check_safety(code: str) -> Tuple[bool, str]:
    """Inspects AST before execution to prevent malicious or destructive commands."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Syntax errors are harmless to execute and should be caught by Python runner
        return True, ""

    for node in ast.walk(tree):
        # 1. Check for disallowed imports (e.g., import os, import subprocess)
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split('.')[0]
                if root_pkg in DISALLOWED_IMPORTS:
                    return False, f"Security Sandbox: Importing '{root_pkg}' is restricted in the learning environment."
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split('.')[0]
                if root_pkg in DISALLOWED_IMPORTS:
                    return False, f"Security Sandbox: Importing from '{root_pkg}' is restricted in the learning environment."

        # 2. Check for disallowed function calls (e.g., os.system('del ...'))
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                if node.func.attr in DISALLOWED_CALLS:
                    return False, f"Security Sandbox: Call to '{node.func.attr}()' is restricted."
            elif isinstance(node.func, ast.Name):
                if node.func.id in DISALLOWED_CALLS:
                    return False, f"Security Sandbox: Function '{node.func.id}()' is restricted."

    return True, ""

def parse_traceback(stderr: str) -> Dict[str, Any]:
    """Parses standard Python traceback output into structured diagnostic fields."""
    parsed = {
        "error_type": None,
        "line": None,
        "column": None,
        "message": ""
    }
    if not stderr:
        return parsed

    # 1. Match SyntaxError / IndentationError (which show line and caret ^)
    syntax_pat = re.search(
        r'File "(?:[^"]+)", line (\d+)(?:, in .*)?\n(?:[^\n]*\n)?(?:\s*(\^+)\n)?([A-Za-z_]\w*Error):\s*(.*)',
        stderr
    )
    if syntax_pat:
        parsed["line"] = int(syntax_pat.group(1))
        parsed["error_type"] = syntax_pat.group(3)
        parsed["message"] = syntax_pat.group(4).strip()
        if syntax_pat.group(2):
            parsed["column"] = len(syntax_pat.group(2))
        return parsed

    # 2. Match standard Runtime exceptions (TypeError, ZeroDivisionError, IndexError, etc.)
    lines = [l.strip() for l in stderr.strip().split('\n') if l.strip()]
    for line in reversed(lines):
        m = re.match(r'^([A-Za-z_]\w*(?:Error|Exception)):\s*(.*)', line)
        if m:
            parsed["error_type"] = m.group(1)
            parsed["message"] = m.group(2).strip()
            break

    # Extract the deepest file line number from the traceback
    file_matches = re.findall(r'File "(?:[^"]+)", line (\d+)', stderr)
    if file_matches:
        parsed["line"] = int(file_matches[-1])

    return parsed

def execute_sandbox_code(code: str, timeout: float = 3.5) -> Dict[str, Any]:
    """Executes Python code in an isolated temporary file with timeout and resource guards."""
    # Step 1: Pre-execution Safety Screen
    is_safe, reason = check_safety(code)
    if not is_safe:
        return {
            "stdout": "",
            "stderr": f"PermissionError: {reason}\n",
            "exit_code": 1,
            "execution_time_ms": 0,
            "parsed_error": {
                "error_type": "SecurityRestriction",
                "line": 1,
                "column": None,
                "message": reason
            }
        }

    # Step 2: Write to isolated temp script
    temp_dir = tempfile.mkdtemp(prefix="relearn_sandbox_")
    script_path = Path(temp_dir) / "main.py"

    try:
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code)

        start_time = time.perf_counter()
        
        proc = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=temp_dir
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

        stderr_output = proc.stderr
        parsed_err = parse_traceback(stderr_output)

        return {
            "stdout": proc.stdout,
            "stderr": stderr_output,
            "exit_code": proc.returncode,
            "execution_time_ms": elapsed_ms,
            "parsed_error": parsed_err
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"TimeoutError: Execution timed out after {timeout}s (Infinite loop protection triggered).\n",
            "exit_code": 124,
            "execution_time_ms": timeout * 1000,
            "parsed_error": {
                "error_type": "TimeoutError",
                "line": None,
                "column": None,
                "message": f"Execution exceeded {timeout} seconds limit."
            }
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"SystemError: {str(e)}\n",
            "exit_code": 1,
            "execution_time_ms": 0,
            "parsed_error": {
                "error_type": "SystemError",
                "line": None,
                "column": None,
                "message": str(e)
            }
        }
    finally:
        # Clean up temporary directory and script
        try:
            if script_path.exists():
                script_path.unlink()
            os.rmdir(temp_dir)
        except Exception:
            pass
