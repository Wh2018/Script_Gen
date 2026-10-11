"""
主工作流
整合政策解析和剧本生成的完整流程
"""
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from ..parsers.policy_parser import PolicyParser
from ..generators.script_generator import ScriptGenerator
from ..utils.output_formatter import OutputFormatter


class ScriptGenerationWorkflow:
    """剧本生成工作流"""

    def __init__(self):
        self.policy_parser = PolicyParser()
        self.script_generator = ScriptGenerator()

    def run(
        self,
        input_files: List[str],
        output_dir: str = "output",
        save_analysis: bool = True,
        duration: Optional[int] = None
    ) -> Dict:
        """
        运行完整的剧本生成工作流

        Args:
            input_files: 输入文件路径列表
            output_dir: 输出目录
            save_analysis: 是否保存政策分析报告
            duration: 指定剧本总时长（正整数秒）；None表示自动估算

        Returns:
            结果字典，包含生成的文件路径
        """
        if duration is not None and (type(duration) is not int or duration <= 0):
            raise ValueError("剧本时长必须为正整数（单位：秒）")

        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 步骤1：政策语义解析
        policy_analysis = self.policy_parser.parse_policies(input_files)

        # 步骤2：剧本生成
        script_data = self.script_generator.generate_script(
            policy_analysis, duration=duration
        )

        # 步骤3：输出文件
        print("\n" + "="*70)
        print("💾 第三步：保存输出文件")
        print("="*70)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存剧本
        script_file = output_path / f"微短剧剧本_{timestamp}.md"
        script_markdown = OutputFormatter.format_script_to_markdown(script_data)

        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_markdown)

        print(f"\n✓ 剧本已保存: {script_file}")

        result = {
            'script_file': str(script_file.name)
        }

        # 保存政策分析报告（可选）
        if save_analysis:
            analysis_file = output_path / f"政策分析报告_{timestamp}.md"
            analysis_markdown = OutputFormatter.format_policy_analysis_to_markdown(
                policy_analysis
            )

            with open(analysis_file, 'w', encoding='utf-8') as f:
                f.write(analysis_markdown)

            print(f"✓ 政策分析报告已保存: {analysis_file}")

            result['analysis_file'] = str(analysis_file.name)

        return result
