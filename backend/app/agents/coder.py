"""
编码Agent - 配备Python代码执行工具
"""
from app.agents.base import BaseAgent
from app.tools.code_executor import CodeExecutorTools
from langchain_openai import ChatOpenAI

def get_coder_agent(model: ChatOpenAI):
    """创建配备代码执行工具的编码Agent"""
    code_tools = CodeExecutorTools()
    
    return BaseAgent(
        name="coder",
        model=model,
        system_prompt=(
            "你是一名专业的Python程序员。你的任务是:\n"
            "1. 编写清晰、高效、有注释的Python代码\n"
            "2. 使用execute_python工具运行代码验证正确性\n"
            "3. 调试错误并给出修复方案\n"
            "4. 遵循PEP 8编码规范\n\n"
            "注意: 代码执行有安全限制，禁止文件操作、系统调用等危险操作。"
        ),
        tools=code_tools.get_tools()
    )

