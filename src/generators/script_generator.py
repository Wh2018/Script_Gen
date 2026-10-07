"""
剧本生成模块

负责根据政策分析生成微短剧剧本
"""

from typing import Dict
from ..models.llm_client import get_llm_client
from ..models.schemas import NarrativeFramework, ScriptContent


class ScriptGenerator:
    """剧本生成器"""

    def __init__(self):
        """初始化剧本生成器"""
        self.llm_client = get_llm_client()

    def generate_script(self, policy_analysis: Dict) -> Dict:
        """
        生成完整剧本

        Args:
            policy_analysis: 政策分析结果

        Returns:
            剧本字典
        """
        print("\n" + "="*70)
        print("🎬 第二步：微短剧剧本生成")
        print("="*70)

        # 步骤1: 设计叙事框架
        print("\n📐 设计叙事框架...")
        narrative = self._design_narrative(policy_analysis)

        if not narrative:
            raise ValueError("叙事框架设计失败")

        print(f"  ✓ 叙事框架设计完成")
        print(f"    • 预估时长: {narrative.get('estimated_duration', 'N/A')}秒")
        print(f"    • 情感基调: {narrative.get('emotional_tone', 'N/A')[:30]}...")

        # 步骤2: 生成详细剧本
        print("\n✍️  生成详细剧本...")
        script = self._generate_detailed_script(policy_analysis, narrative)

        if not script:
            raise ValueError("剧本生成失败")

        print(f"  ✓ 剧本生成完成")
        print(f"    • 角色数: {len(script.get('characters', []))}")
        print(f"    • 场景数: {len(script.get('scenes', []))}")
        print(f"    • 镜头数: {len(script.get('shots', []))}")

        return {
            'narrative': narrative,
            'script': script,
            'policy_analysis': policy_analysis
        }

    def _design_narrative(self, policy_analysis: Dict) -> Dict:
        """
        设计叙事框架

        Args:
            policy_analysis: 政策分析结果

        Returns:
            叙事框架字典
        """
        # 加载提示词模板
        prompt_template = self.llm_client.load_prompt_template('narrative_design')

        # 准备政策数据
        import json

        # 根据分析类型提取政策信息
        if policy_analysis['type'] == 'synthesis':
            # 多政策综合
            policy_data = {
                'summary': policy_analysis['synthesis']['overall_summary'],
                'themes': policy_analysis['synthesis']['common_themes'],
                'key_points': policy_analysis['synthesis']['synthesized_key_points']
            }
        else:
            # 单政策
            policy = policy_analysis['policy']
            policy_data = {
                'summary': policy['policy_summary'],
                'background': policy['background'],
                'goal': policy['core_goal'],
                'key_points': policy['key_points']
            }

        policy_json = json.dumps(policy_data, ensure_ascii=False, indent=2)

        # 填充模板
        prompt = prompt_template.replace('{policy_json}', policy_json)

        # 调用LLM
        result = self.llm_client.structured_output(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            schema=NarrativeFramework,
            temperature=0.8,
            max_retries=3
        )

        if result:
            return result.model_dump()
        else:
            return None

    def _generate_detailed_script(self, policy_analysis: Dict, narrative: Dict) -> Dict:
        """
        生成详细剧本

        Args:
            policy_analysis: 政策分析结果
            narrative: 叙事框架

        Returns:
            剧本字典
        """
        # 加载提示词模板
        prompt_template = self.llm_client.load_prompt_template('script_generation')

        # 准备数据
        import json

        # 准备政策数据
        if policy_analysis['type'] == 'synthesis':
            policy_data = {
                'summary': policy_analysis['synthesis']['overall_summary'],
                'themes': policy_analysis['synthesis']['common_themes'],
                'key_points': policy_analysis['synthesis']['synthesized_key_points']
            }
        else:
            policy = policy_analysis['policy']
            policy_data = {
                'summary': policy['policy_summary'],
                'background': policy['background'],
                'goal': policy['core_goal'],
                'key_points': policy['key_points'],
                'measures': policy.get('policy_measures', [])[:5]
            }

        policy_json = json.dumps(policy_data, ensure_ascii=False, indent=2)
        narrative_json = json.dumps(narrative, ensure_ascii=False, indent=2)

        # 填充模板
        prompt = prompt_template.replace('{policy_json}', policy_json)
        prompt = prompt.replace('{narrative_json}', narrative_json)
        prompt = prompt.replace('{duration}', str(narrative.get('estimated_duration', 60)))

        # 调用LLM（使用更高的max_tokens）
        result = self.llm_client.structured_output(
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            schema=ScriptContent,
            temperature=0.8,
            max_tokens=12000,  # 增加token限制以支持详细的剧本
            max_retries=3
        )

        if result:
            return result.model_dump()
        else:
            return None
