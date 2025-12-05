"""
代码执行工具 - 安全的Python REPL
"""
from typing import List
from langchain_experimental.utilities import PythonREPL
from langchain_core.tools import tool
import re

# 初始化REPL
_repl_instance = PythonREPL()

# 危险操作黑名单
_forbidden_patterns = [
    r'os\.system',
    r'subprocess',
    r'eval\(',
    r'exec\(',
    r'__import__',
    r'open\(',  # 文件操作需谨慎
    r'rm\s+-rf',
]

def _is_safe_code(code: str) -> tuple[bool, str]:
    """检查代码安全性"""
    for pattern in _forbidden_patterns:
        if re.search(pattern, code, re.IGNORECASE):
            return False, f"代码包含危险操作: {pattern}"
    
    # 检查代码长度
    if len(code) > 5000:
        return False, "代码过长（超过5000字符）"
    
    return True, ""

@tool
def execute_python(code: str) -> str:
    """
    执行Python代码并返回结果
    
    Args:
        code: Python代码字符串
        
    Returns:
        执行结果或错误信息
        
    Example:
        execute_python("print(2 + 2)")
        # Output: "4"
    """
    # 安全检查
    is_safe, error_msg = _is_safe_code(code)
    if not is_safe:
        return f"❌ 安全检查失败: {error_msg}"
    
    try:
        result = _repl_instance.run(code)
        
        # 如果结果为空，说明没有输出
        if not result or result.strip() == "":
            return "✅ 代码执行成功（无输出）"
        
        return f"✅ 执行成功:\n{result}"
        
    except SyntaxError as e:
        return f"❌ 语法错误:\n{str(e)}"
    except Exception as e:
        return f"❌ 运行时错误:\n{type(e).__name__}: {str(e)}"

class CodeExecutorTools:
    """代码执行工具类 - 提供工具列表"""
    
    def get_tools(self):
        """返回可用工具列表"""
        return [execute_python]



# 使用示例
"""
from app.tools.code_executor import CodeExecutorTools

code_tools = CodeExecutorTools()
tools = code_tools.get_tools()

# 在Agent中绑定工具
model_with_tools = model.bind_tools(tools)
"""

