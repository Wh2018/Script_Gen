"""
政策语义解析模块

负责解析政策文本，提取关键信息
"""

from typing import List, Dict
from ..models.llm_client import get_llm_client
from ..models.schemas import PolicyAnalysis, PolicySynthesis
from ..utils.text_processor import TextProcessor


class PolicyParser:
    """政策解析器"""

    def __init__(self):
        """初始化政策解析器"""
        self.llm_client = get_llm_client()
        self.text_processor = TextProcessor()

    def parse_policies(self, file_paths: List[str]) -> Dict:
        """
        解析多个政策文件

        Args:
            file_paths: 政策文件路径列表

        Returns:
            综合分析结果字典
        """
        print("\n" + "="*70)
        print("📋 第一步：政策语义解析")
        print("="*70)

        all_policies = []

        # 读取所有文件
        print(f"\n📖 读取 {len(file_paths)} 个文件...")
        for file_path in file_paths:
            print(f"  • 读取文件: {file_path}")
            file_data = self.text_processor.read_file(file_path)

            # 从文件中分割多个政策
            policies = self.text_processor.split_policies(file_data['content'])
            print(f"    ✓ 识别到 {len(policies)} 个政策文档")

            all_policies.extend(policies)

        print(f"\n📊 共识别 {len(all_policies)} 个政策文档")

        # 分析每个政策
        analyzed_policies = []

        for i, policy in enumerate(all_policies, 1):
            print(f"\n--- 分析政策 {i}/{len(all_policies)}: {policy['title'][:30]}... ---")

            result = self._analyze_single_policy(policy['content'])
            if result:
                analyzed_policies.append(result)
                print(f"  ✓ 分析完成")
            else:
                print(f"  ✗ 分析失败，跳过此政策")

        if not analyzed_policies:
            raise ValueError("没有成功分析任何政策")

        # 如果有多个政策，进行综合分析
        if len(analyzed_policies) > 1:
            print(f"\n🔄 综合分析 {len(analyzed_policies)} 个政策...")
            synthesis_result = self._synthesize_policies(analyzed_policies)

            return {
                'type': 'synthesis',
                'individual_policies': analyzed_policies,
                'synthesis': synthesis_result,
                'total_count': len(analyzed_policies)
            }
        else:
            print(f"\n✓ 单个政策分析完成")
            return {
                'type': 'single',
                'policy': analyzed_policies[0],
                'total_count': 1
            }

    def _analyze_single_policy(self, policy_text: str) -> Dict:
        """
        分析单个政策

        Args:
            policy_text: 政策文本

        Returns:
            分析结果字典
        """
        # 检查文本长度
        if len(policy_text) > 8000:
            print(f"  ⚠ 文本过长 ({len(policy_text)} 字符)，进行分块处理...")
            return self._analyze_long_policy(policy_text)

        # 加载提示词模板
        prompt_template = self.llm_client.load_prompt_template('policy_analysis')

        # 填充模板
        prompt = prompt_template.replace('{policy_text}', policy_text)

        # 调用LLM
        print(f"  🤖 调用大模型分析...")

        result = self.llm_client.structured_output(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            schema=PolicyAnalysis,
            temperature=0.7,
            max_retries=3
        )

        if result:
            return result.model_dump()
        else:
            return None

    def _analyze_long_policy(self, policy_text: str) -> Dict:
        """
        分析超长政策文本（分块处理）

        Args:
            policy_text: 政策文本

        Returns:
            分析结果字典
        """
        # 分块
        chunks = self.text_processor.chunk_text(policy_text, max_length=7000)
        print(f"  📑 分为 {len(chunks)} 个块")

        # 分析每个块
        chunk_results = []

        for i, chunk in enumerate(chunks, 1):
            print(f"    • 分析第 {i}/{len(chunks)} 块...")

            prompt_template = self.llm_client.load_prompt_template('policy_analysis')
            prompt = prompt_template.replace('{policy_text}', chunk)

            result = self.llm_client.structured_output(
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                schema=PolicyAnalysis,
                temperature=0.7,
                max_retries=3
            )

            if result:
                chunk_results.append(result.model_dump())
                print(f"      ✓ 完成")
            else:
                print(f"      ✗ 失败")

        if not chunk_results:
            return None

        # 合并结果
        print(f"  🔄 合并分块结果...")
        merged_result = self.text_processor.merge_chunked_analysis(chunk_results)

        return merged_result

    def _synthesize_policies(self, policies: List[Dict]) -> Dict:
        """
        综合分析多个政策

        Args:
            policies: 政策分析结果列表

        Returns:
            综合分析结果字典
        """
        # 加载提示词模板
        prompt_template = self.llm_client.load_prompt_template('policy_synthesis')

        # 构造政策JSON
        import json
        policies_json = json.dumps(policies, ensure_ascii=False, indent=2)

        # 如果太长，需要精简
        if len(policies_json) > 10000:
            # 只保留关键字段
            simplified_policies = []
            for p in policies:
                simplified_policies.append({
                    'policy_title': p.get('policy_title', ''),
                    'policy_summary': p.get('policy_summary', ''),
                    'core_goal': p.get('core_goal', ''),
                    'key_points': p.get('key_points', [])
                })
            policies_json = json.dumps(simplified_policies, ensure_ascii=False, indent=2)

        # 填充模板
        prompt = prompt_template.replace('{policies_json}', policies_json)

        # 调用LLM
        print(f"  🤖 调用大模型进行综合分析...")

        result = self.llm_client.structured_output(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            schema=PolicySynthesis,
            temperature=0.7,
            max_retries=3
        )

        if result:
            print(f"  ✓ 综合分析完成")
            return result.model_dump()
        else:
            print(f"  ✗ 综合分析失败，使用基础合并")
            # 降级方案：简单合并
            return self._simple_synthesis(policies)

    def _simple_synthesis(self, policies: List[Dict]) -> Dict:
        """
        简单的政策综合（降级方案）

        Args:
            policies: 政策分析结果列表

        Returns:
            综合结果字典
        """
        all_key_points = []
        for p in policies:
            all_key_points.extend(p.get('key_points', []))

        # 去重并限制数量
        unique_points = list(dict.fromkeys(all_key_points))[:10]

        return {
            'overall_summary': '本次分析涵盖多个相关政策文件，涉及政策的制定背景、核心目标、实施措施等多个方面。',
            'common_themes': ['政策宣传', '规范管理', '创新发展'],
            'synthesized_key_points': unique_points
        }
