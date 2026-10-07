"""
LLM客户端封装
支持DeepSeek和其他OpenAI兼容API
"""
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel
import json
import time
from pathlib import Path
from openai import OpenAI

from .config import get_config


class LLMClient:
    """LLM客户端"""

    def __init__(self):
        """初始化LLM客户端"""
        config = get_config()
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_base
        )
        self.model = config.model
        self.default_temperature = 0.7
        self.default_max_tokens = 8192
        self.prompts_dir = Path(__file__).parent.parent.parent / "prompts"

    def load_prompt_template(self, template_name: str) -> str:
        """
        从文件加载提示词模板

        Args:
            template_name: 模板名称（不含.txt后缀）

        Returns:
            提示词模板内容
        """
        template_path = self.prompts_dir / f"{template_name}.txt"

        if not template_path.exists():
            raise FileNotFoundError(f"提示词模板不存在: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        **kwargs
    ) -> str:
        """
        基础对话接口（带重试）

        Args:
            messages: 消息列表，格式 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）

        Returns:
            模型回复文本
        """
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature or self.default_temperature,
                    max_tokens=max_tokens or self.default_max_tokens,
                    **kwargs
                )
                return response.choices[0].message.content

            except Exception as e:
                last_error = e
                print(f"  ⚠ API调用失败 (第{attempt + 1}次): {str(e)[:100]}")

                if attempt < max_retries - 1:
                    print(f"  ⏳ {retry_delay:.1f}秒后重试...")
                    time.sleep(retry_delay)
                    retry_delay *= 1.5  # 指数退避

        raise RuntimeError(f"LLM调用失败（重试{max_retries}次后）: {last_error}")

    def structured_output(
        self,
        messages: List[Dict[str, str]],
        schema: Type[BaseModel],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        max_retries: int = 3
    ) -> BaseModel:
        """
        结构化输出接口（带重试和错误恢复）

        Args:
            messages: 消息列表
            schema: Pydantic模型类
            temperature: 温度参数
            max_tokens: 最大token数
            max_retries: 最大重试次数

        Returns:
            解析后的Pydantic模型实例
        """
        # 获取schema的JSON Schema定义
        schema_json = schema.model_json_schema()
        schema_str = json.dumps(schema_json, ensure_ascii=False, indent=2)

        # 在system message中加入schema指示
        schema_instruction = f"""
你必须以JSON格式输出，严格遵循以下JSON Schema。
直接输出JSON，不要有任何其他文字。确保JSON完整且可解析。

JSON Schema定义：
{schema_str}

输出格式要求：
1. 直接输出JSON对象，以{{开头，以}}结尾
2. 不要输出markdown代码块标记
3. 确保所有字符串值用双引号包裹
4. 确保JSON结构完整，所有括号匹配
5. 所有必需字段都必须提供值
6. 字段名称和数据类型必须与schema完全一致

请开始输出JSON：
"""

        # 修改system message
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[0]["role"] == "system":
            enhanced_messages[0]["content"] += "\n\n" + schema_instruction
        else:
            enhanced_messages.insert(0, {
                "role": "system",
                "content": schema_instruction
            })

        # 尝试调用并解析
        last_error = None
        for attempt in range(max_retries):
            try:
                response_text = self.chat(
                    enhanced_messages,
                    temperature=temperature,
                    max_tokens=max_tokens or 8192,
                    max_retries=2  # chat内部也有重试
                )

                # 提取JSON
                json_str = self._extract_json(response_text)

                # 解析为Pydantic模型
                return schema.model_validate_json(json_str)

            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    print(f"    ⚠ 解析失败，重试第 {attempt + 2} 次...")
                    # 添加错误提示，让模型重新生成
                    enhanced_messages.append({
                        "role": "assistant",
                        "content": response_text[:500] if 'response_text' in locals() else ""
                    })
                    enhanced_messages.append({
                        "role": "user",
                        "content": f"输出格式不正确: {str(e)[:100]}\n请重新生成完整的JSON，确保：1.以{{开头以}}结尾 2.所有必需字段都有值 3.JSON格式正确"
                    })
                    time.sleep(1)
                    continue

        raise RuntimeError(f"结构化输出解析失败（重试{max_retries}次后）: {last_error}")

    def _extract_json(self, text: str) -> str:
        """
        从文本中提取JSON

        Args:
            text: 包含JSON的文本

        Returns:
            提取的JSON字符串
        """
        import re

        text = text.strip()

        # 尝试直接解析
        if text.startswith('{') and text.endswith('}'):
            try:
                json.loads(text)  # 验证
                return text
            except:
                pass

        if text.startswith('[') and text.endswith(']'):
            try:
                json.loads(text)  # 验证
                return text
            except:
                pass

        # 尝试从markdown代码块中提取
        json_pattern = r'```(?:json)?\s*(\{.*\})\s*```'
        matches = re.findall(json_pattern, text, re.DOTALL)
        if matches:
            candidate = max(matches, key=len)
            try:
                json.loads(candidate)
                return candidate
            except:
                pass

        # 尝试查找第一个 { 到最后一个 } 的内容
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            potential_json = text[first_brace:last_brace+1]
            # 验证是否是有效的JSON结构
            try:
                json.loads(potential_json)
                return potential_json
            except:
                pass

        # 如果都失败，返回原文本（会在外层抛出错误）
        return text

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        流式对话接口

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Yields:
            流式输出的文本片段
        """
        try:
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.default_temperature,
                max_tokens=max_tokens or self.default_max_tokens,
                stream=True,
                **kwargs
            )

            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"流式LLM调用失败: {e}")


# 全局客户端实例
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """获取全局LLM客户端实例（单例模式）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = LLMClient()
    return _llm_client
