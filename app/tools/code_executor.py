from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import Tool

def get_code_executor_tool():
    """
    Returns a tool that can execute Python code.
    WARNING: This executes code locally. Use with caution.
    """
    repl = PythonREPL()
    
    def python_repl(code: str):
        try:
            result = repl.run(code)
            return f"Successfully executed:\n{result}"
        except Exception as e:
            return f"Failed to execute:\n{e}"

    return Tool(
        name="python_repl",
        description="A Python shell. Use this to execute python commands. Input should be a valid python command. If you want to see the output of a value, you should print it out with `print(...)`.",
        func=python_repl
    )
