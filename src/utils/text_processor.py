"""
文本处理工具模块

支持多种格式的文本文件读取和处理
"""

import re
from pathlib import Path
from typing import List, Dict
import chardet


class TextProcessor:
    """文本处理器"""

    @staticmethod
    def read_file(file_path: str) -> Dict[str, str]:
        """
        读取文件内容

        Args:
            file_path: 文件路径

        Returns:
            字典，包含 'content' 和 'metadata'
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 根据文件扩展名选择读取方式
        ext = path.suffix.lower()

        if ext in ['.txt', '.md']:
            content = TextProcessor._read_text_file(path)
        elif ext == '.docx':
            content = TextProcessor._read_docx_file(path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

        return {
            'content': content,
            'metadata': {
                'filename': path.name,
                'size': len(content),
                'format': ext
            }
        }

    @staticmethod
    def _read_text_file(path: Path) -> str:
        """读取文本文件"""
        # 检测编码
        with open(path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'

        # 读取内容
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()

        return TextProcessor._clean_text(content)

    @staticmethod
    def _read_docx_file(path: Path) -> str:
        """读取Word文档"""
        try:
            from docx import Document
        except ImportError:
            raise ImportError("请安装 python-docx: pip install python-docx")

        doc = Document(path)
        content = '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])

        return TextProcessor._clean_text(content)

    @staticmethod
    def _clean_text(text: str) -> str:
        """清理文本"""
        # 移除多余的空白字符
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = text.strip()

        return text

    @staticmethod
    def split_policies(text: str) -> List[Dict[str, str]]:
        """
        从文本中分割多个政策文档

        支持以下分割标记：
        - ## 标题（Markdown二级标题）
        - 一、二、三... 标题
        - 【标题】

        Args:
            text: 输入文本

        Returns:
            政策列表，每个政策包含 'title' 和 'content'
        """
        policies = []

        # 尝试用Markdown二级标题分割
        sections = re.split(r'\n##\s+', text)

        if len(sections) > 1:
            # 第一部分可能是前言，如果太短就跳过
            start_idx = 0
            if len(sections[0].strip()) < 100:
                start_idx = 1

            for i in range(start_idx, len(sections)):
                section = sections[i].strip()
                if not section:
                    continue

                # 提取标题（第一行）
                lines = section.split('\n', 1)
                title = lines[0].strip()
                content = lines[1].strip() if len(lines) > 1 else section

                # 过滤掉太短的部分（可能不是完整政策）
                if len(content) >= 200:
                    policies.append({
                        'title': title,
                        'content': section
                    })

        # 尝试用中文序号分割
        if len(policies) == 0:
            sections = re.split(r'\n[一二三四五六七八九十]+、', text)

            if len(sections) > 1:
                start_idx = 0
                if len(sections[0].strip()) < 100:
                    start_idx = 1

                for i in range(start_idx, len(sections)):
                    section = sections[i].strip()
                    if not section or len(section) < 200:
                        continue

                    # 提取标题（第一行或前几个字）
                    lines = section.split('\n', 1)
                    title = lines[0][:50].strip()

                    policies.append({
                        'title': title,
                        'content': section
                    })

        # 如果没有找到分割点，将整个文本作为一个政策
        if len(policies) == 0:
            # 尝试提取标题
            title = TextProcessor._extract_title(text)
            policies.append({
                'title': title,
                'content': text
            })

        return policies

    @staticmethod
    def _extract_title(text: str) -> str:
        """从文本中提取标题"""
        lines = text.split('\n')

        for line in lines[:10]:  # 只检查前10行
            line = line.strip()

            # 跳过空行和太短的行
            if not line or len(line) < 5:
                continue

            # 跳过元数据行
            if line.startswith('**') or line.startswith('来源') or line.startswith('发布'):
                continue

            # 如果是Markdown标题
            if line.startswith('#'):
                return line.lstrip('#').strip()

            # 如果包含《》
            match = re.search(r'《(.+?)》', line)
            if match:
                return match.group(1)

            # 返回第一个看起来像标题的行
            if len(line) <= 50 and not line.endswith('。'):
                return line

        return "政策文件"

    @staticmethod
    def chunk_text(text: str, max_length: int = 8000) -> List[str]:
        """
        将超长文本分块

        Args:
            text: 输入文本
            max_length: 每块最大长度

        Returns:
            文本块列表
        """
        if len(text) <= max_length:
            return [text]

        chunks = []

        # 按段落分割
        paragraphs = text.split('\n\n')

        current_chunk = ""
        for para in paragraphs:
            # 如果单个段落就超长，需要进一步切分
            if len(para) > max_length:
                # 先保存当前块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""

                # 切分长段落
                sentences = re.split(r'([。！？\n])', para)
                temp = ""
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""

                    if len(temp) + len(sentence) + len(delimiter) > max_length:
                        if temp:
                            chunks.append(temp.strip())
                        temp = sentence + delimiter
                    else:
                        temp += sentence + delimiter

                if temp:
                    current_chunk = temp

            # 正常段落处理
            elif len(current_chunk) + len(para) + 2 <= max_length:
                current_chunk += para + "\n\n"
            else:
                chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    @staticmethod
    def merge_chunked_analysis(chunks_results: List[Dict]) -> Dict:
        """
        合并分块分析的结果

        Args:
            chunks_results: 每个文本块的分析结果列表

        Returns:
            合并后的分析结果
        """
        if len(chunks_results) == 1:
            return chunks_results[0]

        # 合并策略：
        # - 标题：使用第一块的
        # - 摘要：合并所有摘要
        # - 背景：使用最长的
        # - 目标：合并
        # - 意义：使用最长的
        # - 主体/对象/措施：去重合并
        # - 要点：去重合并（最多10个）

        merged = {
            'policy_title': chunks_results[0].get('policy_title', ''),
            'policy_summary': ' '.join([r.get('policy_summary', '') for r in chunks_results])[:200],
            'background': max([r.get('background', '') for r in chunks_results], key=len),
            'core_goal': ' '.join([r.get('core_goal', '') for r in chunks_results])[:150],
            'social_significance': max([r.get('social_significance', '') for r in chunks_results], key=len),
            'policy_subject': [],
            'policy_object': [],
            'policy_measures': [],
            'key_points': []
        }

        # 合并列表字段（去重）
        for field in ['policy_subject', 'policy_object', 'policy_measures', 'key_points']:
            items = []
            seen = set()
            for result in chunks_results:
                for item in result.get(field, []):
                    if item not in seen:
                        items.append(item)
                        seen.add(item)

            # 限制数量
            if field == 'key_points':
                merged[field] = items[:10]
            elif field == 'policy_measures':
                merged[field] = items[:12]
            else:
                merged[field] = items[:8]

        return merged
