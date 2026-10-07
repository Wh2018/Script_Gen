"""
输出格式化模块

负责将剧本数据格式化为Markdown文档
"""

from typing import Dict, List
from datetime import datetime


class OutputFormatter:
    """输出格式化器"""

    @staticmethod
    def format_script_to_markdown(script_data: Dict) -> str:
        """
        将剧本数据格式化为Markdown

        Args:
            script_data: 完整的剧本数据

        Returns:
            Markdown格式的剧本文本
        """
        md_lines = []

        narrative = script_data['narrative']
        script = script_data['script']

        # 标题
        md_lines.append("# 政策宣传微短剧剧本")
        md_lines.append("")

        # 剧本题目
        script_title = script.get('title', '未命名')
        md_lines.append(f"## {script_title}")
        md_lines.append("")

        # 剧本信息
        md_lines.append("## 剧本信息")
        md_lines.append("")
        md_lines.append(f"**预估时长**: {narrative.get('estimated_duration', 'N/A')}秒")
        md_lines.append("")
        md_lines.append(f"**情感基调**: {narrative.get('emotional_tone', 'N/A')}")
        md_lines.append("")

        # 故事角度
        md_lines.append("## 故事角度")
        md_lines.append("")
        md_lines.append(narrative.get('story_angle', ''))
        md_lines.append("")

        # 叙事结构
        md_lines.append("## 叙事结构")
        md_lines.append("")
        structure = narrative.get('narrative_structure', {})
        if structure:
            md_lines.append("### 开端")
            md_lines.append(structure.get('opening', ''))
            md_lines.append("")
            md_lines.append("### 发展")
            md_lines.append(structure.get('development', ''))
            md_lines.append("")
            md_lines.append("### 高潮")
            md_lines.append(structure.get('climax', ''))
            md_lines.append("")
            md_lines.append("### 结局")
            md_lines.append(structure.get('ending', ''))
            md_lines.append("")

        # 角色设定
        md_lines.append("## 角色设定")
        md_lines.append("")

        for i, character in enumerate(script.get('characters', []), 1):
            md_lines.append(f"### 角色{i}：{character.get('name', 'N/A')}")
            md_lines.append("")
            md_lines.append(f"**角色类型**: {character.get('role_type', 'N/A')}")
            md_lines.append("")
            md_lines.append(f"**角色描述**:")
            md_lines.append(character.get('description', ''))
            md_lines.append("")
            md_lines.append(f"**外貌服装**:")
            md_lines.append(character.get('appearance', ''))
            md_lines.append("")

        # 场景设计
        md_lines.append("## 场景设计")
        md_lines.append("")

        for i, scene in enumerate(script.get('scenes', []), 1):
            md_lines.append(f"### 场景{i}：{scene.get('location', 'N/A')}")
            md_lines.append("")
            md_lines.append(f"**时间**: {scene.get('time_of_day', 'N/A')}")
            md_lines.append("")
            md_lines.append(f"**预计时长**: {scene.get('estimated_duration', 'N/A')}秒")
            md_lines.append("")
            md_lines.append(f"**环境描述**:")
            md_lines.append(scene.get('environment_description', ''))
            md_lines.append("")

        # 完整剧本（分镜脚本）
        md_lines.append("## 完整剧本（分镜脚本）")
        md_lines.append("")

        # 按场景组织镜头
        scenes_dict = {scene['scene_id']: scene for scene in script.get('scenes', [])}
        shots_by_scene = {}

        for shot in script.get('shots', []):
            scene_id = shot.get('scene_id', 'unknown')
            if scene_id not in shots_by_scene:
                shots_by_scene[scene_id] = []
            shots_by_scene[scene_id].append(shot)

        # 输出每个场景的镜头
        for scene in script.get('scenes', []):
            scene_id = scene['scene_id']
            scene_shots = shots_by_scene.get(scene_id, [])

            if not scene_shots:
                continue

            md_lines.append(f"### {scene.get('location', scene_id)}")
            md_lines.append("")

            for shot in scene_shots:
                shot_id = shot.get('shot_id', 'N/A')
                shot_type = shot.get('shot_type', 'N/A')

                md_lines.append(f"#### {shot_id} - {shot_type}")
                md_lines.append("")

                # 画面描述
                md_lines.append("**画面描述**:")
                md_lines.append(shot.get('visual_description', ''))
                md_lines.append("")

                # 动作描述
                md_lines.append("**动作描述**:")
                md_lines.append(shot.get('action_description', ''))
                md_lines.append("")

                # 对话
                dialogues = shot.get('dialogue', [])
                if dialogues:
                    md_lines.append("**对话**:")
                    for dialogue in dialogues:
                        character = dialogue.get('character', 'N/A')
                        text = dialogue.get('text', '')
                        emotion = dialogue.get('emotion', '')
                        delivery = dialogue.get('delivery_note', '')

                        md_lines.append(f"- **{character}** ({emotion}): {text}")
                        if delivery:
                            md_lines.append(f"  *{delivery}*")
                    md_lines.append("")

                # 音效
                sound = shot.get('sound_effects', '')
                if sound:
                    md_lines.append(f"**音效**: {sound}")
                    md_lines.append("")

                # 时长
                duration = shot.get('duration_estimate', 'N/A')
                md_lines.append(f"**预计时长**: {duration}秒")
                md_lines.append("")
                md_lines.append("---")
                md_lines.append("")

        return '\n'.join(md_lines)

    @staticmethod
    def format_policy_analysis_to_markdown(policy_analysis: Dict) -> str:
        """
        将政策分析结果格式化为Markdown

        Args:
            policy_analysis: 政策分析数据

        Returns:
            Markdown格式的分析报告
        """
        md_lines = []

        md_lines.append("# 政策分析报告")
        md_lines.append("")

        if policy_analysis['type'] == 'synthesis':
            # 多政策综合分析
            md_lines.append(f"## 政策概览")
            md_lines.append("")
            md_lines.append(f"本次分析共涵盖 **{policy_analysis['total_count']}** 个政策文档。")
            md_lines.append("")

            # 综合分析
            synthesis = policy_analysis['synthesis']

            md_lines.append("## 综合概述")
            md_lines.append("")
            md_lines.append(synthesis.get('overall_summary', ''))
            md_lines.append("")

            md_lines.append("## 共同主题")
            md_lines.append("")
            for theme in synthesis.get('common_themes', []):
                md_lines.append(f"- {theme}")
            md_lines.append("")

            md_lines.append("## 综合关键要点")
            md_lines.append("")
            for i, point in enumerate(synthesis.get('synthesized_key_points', []), 1):
                md_lines.append(f"{i}. {point}")
            md_lines.append("")

            # 各政策详情
            md_lines.append("## 各政策详情")
            md_lines.append("")

            for i, policy in enumerate(policy_analysis['individual_policies'], 1):
                md_lines.append(f"### 政策{i}：{policy.get('policy_title', 'N/A')}")
                md_lines.append("")
                md_lines.append(f"**摘要**: {policy.get('policy_summary', '')}")
                md_lines.append("")

                md_lines.append("**核心要点**:")
                for point in policy.get('key_points', [])[:5]:
                    md_lines.append(f"- {point}")
                md_lines.append("")

        else:
            # 单政策分析
            policy = policy_analysis['policy']

            md_lines.append(f"## {policy.get('policy_title', '政策文件')}")
            md_lines.append("")

            md_lines.append("### 政策摘要")
            md_lines.append(policy.get('policy_summary', ''))
            md_lines.append("")

            md_lines.append("### 政策背景")
            md_lines.append(policy.get('background', ''))
            md_lines.append("")

            md_lines.append("### 核心目标")
            md_lines.append(policy.get('core_goal', ''))
            md_lines.append("")

            md_lines.append("### 社会意义")
            md_lines.append(policy.get('social_significance', ''))
            md_lines.append("")

            md_lines.append("### 核心要点")
            md_lines.append("")
            for i, point in enumerate(policy.get('key_points', []), 1):
                md_lines.append(f"{i}. {point}")
            md_lines.append("")

        return '\n'.join(md_lines)
