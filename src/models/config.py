"""
配置管理模块
从.env文件读取API配置信息
"""
import os
from pathlib import Path
from typing import Optional


class Config:
    """配置管理类"""

    def __init__(self, api_key: str, api_base: str, model: str):
        self.api_key = api_key
        self.api_base = api_base
        self.model = model

    @classmethod
    def load(cls, env_file: Optional[str] = None) -> "Config":
        """
        从.env文件加载配置

        Args:
            env_file: .env文件路径，默认为项目根目录下的.env

        Returns:
            Config实例
        """
        if env_file is None:
            # 默认从项目根目录读取.env
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / ".env"
        else:
            env_file = Path(env_file)

        # 如果.env文件存在，读取它
        if env_file.exists():
            cls._load_env_file(env_file)

        # 从环境变量读取配置
        api_key = os.getenv("OPENAI_API_KEY")
        api_base = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
        model = os.getenv("OPENAI_MODEL", "gpt-4o")

        if not api_key:
            raise ValueError(
                "未找到API配置。请创建.env文件并设置 OPENAI_API_KEY"
            )

        return cls(api_key=api_key, api_base=api_base, model=model)

    @staticmethod
    def _load_env_file(env_file: Path):
        """
        读取.env文件并设置环境变量

        Args:
            env_file: .env文件路径
        """
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue

                # 解析 KEY=VALUE 格式
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    # 移除引号
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # 设置环境变量（如果尚未设置）
                    if key and not os.getenv(key):
                        os.environ[key] = value

    def __repr__(self) -> str:
        return f"Config(api_base={self.api_base}, model={self.model})"


# 全局配置实例
_config_instance: Optional[Config] = None


def get_config() -> Config:
    """获取全局配置实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config.load()
    return _config_instance
