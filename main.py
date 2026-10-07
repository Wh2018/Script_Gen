"""
主程序入口
政策宣传微短剧剧本生成系统
"""
import sys
import argparse
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.workflows.main_workflow import ScriptGenerationWorkflow


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="政策宣传微短剧剧本生成系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py                                    # 使用默认输入文件 (../Policy_input.md)
  python main.py policy.md                          # 使用单个文件
  python main.py file1.md file2.txt                 # 使用多个文件
  python main.py -i ../Policy_input.md              # 使用 -i 指定输入
  python main.py -o results                         # 指定输出目录
  python main.py policy.md --no-analysis            # 不保存分析报告
        """
    )

    parser.add_argument(
        'input_files',
        nargs='*',
        help='输入的政策文件路径（支持多个文件，可选）'
    )

    parser.add_argument(
        '-i', '--input',
        dest='input_flag',
        action='append',
        help='输入文件（可多次使用，例如: -i file1.md -i file2.md）'
    )

    parser.add_argument(
        '-o', '--output-dir',
        default='output',
        help='输出目录（默认: output）'
    )

    parser.add_argument(
        '--no-analysis',
        action='store_true',
        help='不保存政策分析报告'
    )

    return parser.parse_args()


def main():
    """主函数"""

    # 解析命令行参数
    args = parse_args()

    # 确定输入文件：优先使用 -i 参数，其次使用位置参数，最后使用默认值
    input_files = []
    if args.input_flag:
        input_files.extend(args.input_flag)
    if args.input_files:
        input_files.extend(args.input_files)

    if not input_files:
        # 默认输入文件
        input_files = ["../Policy_input.md"]

    OUTPUT_DIR = args.output_dir
    SAVE_ANALYSIS = not args.no_analysis

    print("="*70)
    print("政策宣传微短剧剧本生成系统".center(60))
    print("="*70)
    print()
    print(f"📥 输入文件: {', '.join(input_files)}")
    print(f"📤 输出目录: {OUTPUT_DIR}")
    print()

    try:
        # 创建工作流实例
        workflow = ScriptGenerationWorkflow()

        # 运行工作流
        result = workflow.run(
            input_files=input_files,
            output_dir=OUTPUT_DIR,
            save_analysis=SAVE_ANALYSIS
        )

        print("\n" + "="*70)
        print("✅ 程序执行成功！")
        print("="*70)
        print(f"\n📁 输出文件位置: {OUTPUT_DIR}/")
        print(f"   • 剧本文件: {result['script_file']}")
        if result.get('analysis_file'):
            print(f"   • 分析报告: {result['analysis_file']}")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断执行")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
