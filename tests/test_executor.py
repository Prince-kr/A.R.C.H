import pytest
from utils.executor import Executor
import os

def test_executor_run_success(tmp_path):
    # Create a dummy script
    script_file = tmp_path / "test_script.py"
    script_file.write_text("print('Hello from script')")
    
    executor = Executor()
    stdout, status = executor.run_script(str(script_file), ["--arg1", "val1"])
    
    assert "Hello from script" in stdout
    assert status == 0

def test_executor_timeout(tmp_path):
    # Create a script that sleeps
    script_file = tmp_path / "sleep_script.py"
    script_file.write_text("import time; time.sleep(5)")
    
    executor = Executor()
    # Run with 1s timeout
    stdout, status = executor.run_script(str(script_file), [], timeout=1)
    
    assert "Timeout" in stdout
    assert status == 1
