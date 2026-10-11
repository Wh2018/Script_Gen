"""
剧本生成模块

负责根据政策分析生成微短剧剧本
"""

from typing import Dict, Optional
from ..models.llm_client import get_llm_client
from ..models.schemas import NarrativeFramework, ScriptContent


class ScriptGenerator:
    """剧本生成器"""

    def __init__(self):
        """初始化剧本生成器"""
        self.llm_client = get_llm_client()

    def generate_script(
        self, policy_analysis: Dict, duration: Optional[int] = None
    ) -> Dict:
        """
        生成完整剧本

        Args:
            policy_analysis: 政策分析结果
            duration: 指定剧本总时长（正整数秒）；None表示自动估算

        Returns:
            剧本字典
        """
        if duration is not None and (type(duration) is not int or duration <= 0):
            raise ValueError("剧本时长必须为正整数（单位：秒）")

        print("\n" + "="*70)
        print("🎬 第二步：微短剧剧本生成")
        print("="*70)

        # 步骤1: 设计叙事框架
        print("\n📐 设计叙事框架...")
        narrative = self._design_narrative(policy_analysis, duration=duration)

        if not narrative:
            raise ValueError("叙事框架设计失败")

        print(f"  ✓ 叙事框架设计完成")
        print(f"    • 预估时长: {narrative.get('estimated_duration', 'N/A')}秒")
        print(f"    • 情感基调: {narrative.get('emotional_tone', 'N/A')[:30]}...")

        # 步骤2: 生成详细剧本
        print("\n✍️  生成详细剧本...")
        script = self._generate_detailed_script(
            policy_analysis, narrative, duration=duration
        )

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

    def _design_narrative(
        self, policy_analysis: Dict, duration: Optional[int] = None
    ) -> Dict:
        """
        设计叙事框架

        Args:
            policy_analysis: 政策分析结果
            duration: 指定剧本总时长（秒）；None表示自动估算

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
        if duration is None:
            duration_requirements = (
                "- 时长：30秒以上，根据政策内容的丰富程度，建议30-90秒\n"
                "- 如果政策内容复杂、信息量大，可以设计60-90秒的剧本\n"
                "- 如果政策内容相对简单，可以设计30-45秒的剧本"
            )
            estimated_duration_requirements = (
                "   - 根据政策内容的丰富程度，建议时长（单位：秒）\n"
                "   - 必须>=30秒\n"
                "   - 给出一个具体的数字，例如45、60、75等"
            )
        else:
            duration_requirements = (
                f"- 用户指定剧本总时长：{duration}秒，必须按此时长规划，"
                "不得根据政策复杂度另行估算、延长或缩短。\n"
                "- 合理分配开端、发展、高潮、结局的时间，在各部分描述中注明预计秒数，"
                f"合计必须为{duration}秒。\n"
                "- 根据指定时长安排情节密度、政策要点数量和叙事节奏；"
                "时长较短时聚焦最关键的政策要点，时长较长时充分展开情节。\n"
                "- 各字段的描述字数是设计说明的篇幅，不代表实际台词字数或播放时长。"
            )
            estimated_duration_requirements = (
                f"   - 使用用户指定值：estimated_duration必须等于{duration}"
                "（单位：秒，整数），不得另行估算。"
            )
        prompt = prompt.replace('{duration_requirements}', duration_requirements)
        prompt = prompt.replace(
            '{estimated_duration_requirements}', estimated_duration_requirements
        )

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
            narrative = result.model_dump()
            if duration is not None:
                # 将指定时长传递给分镜生成及输出，避免模型另行估算覆盖用户输入。
                narrative['estimated_duration'] = duration
            return narrative
        else:
            return None

    def _generate_detailed_script(
        self, policy_analysis: Dict, narrative: Dict, duration: Optional[int] = None
    ) -> Dict:
        """
        生成详细剧本

        Args:
            policy_analysis: 政策分析结果
            narrative: 叙事框架
            duration: 指定剧本总时长（秒）；None表示沿用叙事框架估算值

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
        if duration is None:
            duration_requirements = (
                f"- 目标时长：{narrative.get('estimated_duration', 60)}秒以上\n"
                "- 根据此时长设计合适的场景数量和镜头数量\n"
                "- 30-45秒：建议2-3个场景，4-6个镜头\n"
                "- 45-60秒：建议3-4个场景，6-8个镜头\n"
                "- 60-90秒：建议4-5个场景，8-12个镜头"
            )
            scene_count_requirements = "根据时长设计2-5个场景"
        else:
            duration_requirements = (
                f"- 用户指定总时长：{duration}秒。这是完整剧本的总时长，"
                "不能理解为最低时长，不得自行延长或缩短。\n"
                "- 根据指定时长规划情节、场景数量、镜头数量、台词量和动作节奏，"
                "保证实际内容能够在分配的时间内完成。\n"
                f"- 所有场景的estimated_duration之和必须等于{duration}秒；"
                f"所有镜头的duration_estimate之和也必须等于{duration}秒。\n"
                "- 每个场景的estimated_duration必须等于该场景内所有镜头的"
                "duration_estimate之和，镜头必须归属已定义的场景。\n"
                "- 场景和镜头时长均使用正整数秒。台词按正常中文语速约每秒3-4个字估算，"
                "并为停顿、动作、情绪表达和转场预留时间，避免台词超出镜头时长。\n"
                "- 30-45秒可参考2-3个场景、4-6个镜头；45-60秒可参考3-4个场景、"
                "6-8个镜头；60-90秒可参考4-5个场景、8-12个镜头。"
                "指定时长低于30秒或高于90秒时，按实际时长调整，以上数量仅作参考。\n"
                "- 画面和动作描述的字数是制作说明的篇幅，不代表播放时长；"
                "不要只修改时长数字而让实际台词和动作超时。\n"
                "- 输出前核对场景、镜头的时长总和，以及台词、动作所需时间，"
                "确保与指定时长一致。"
            )
            scene_count_requirements = "按指定总时长安排，通常2-5个场景，必要时可调整"
        prompt = prompt.replace('{duration_requirements}', duration_requirements)
        prompt = prompt.replace('{scene_count_requirements}', scene_count_requirements)

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
