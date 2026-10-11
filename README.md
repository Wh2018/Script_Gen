# 政策宣传微短剧剧本生成系统

基于大语言模型的政策文本智能解析与微短剧剧本自动生成系统。

## 功能特点

- **政策语义解析**：深度理解政策文本，提取核心要点、政策主体/对象、措施等
- **叙事框架设计**：自动设计适合短视频传播的叙事结构
- **详细剧本生成**：生成包含角色、场景、镜头、对话的完整微短剧剧本
- **可选剧本时长**：可指定总时长规划情节与分镜；不指定时根据政策内容自动估算
- **支持多政策综合**：可同时处理多个政策文件，生成综合性剧本

## 系统要求

- Python 3.8+
- conda环境（推荐使用jvben环境）
- 支持OpenAI API的LLM服务（如DeepSeek、OpenAI等）

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API

复制 `.env.example` 为 `.env` 并填入你的API配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

### 3. 运行程序

#### 方式一：使用shell脚本（推荐）

```bash
./run.sh                           # 使用默认输入文件
./run.sh policy.md                 # 指定单个文件
./run.sh file1.md file2.md         # 指定多个文件
./run.sh -i policy.md -o results   # 使用参数
./run.sh policy.md --duration 60   # 指定剧本总时长为60秒
```

#### 方式二：直接运行Python

```bash
python main.py                                    # 使用默认输入 (../Policy_input.md)
python main.py policy.md                          # 单个文件
python main.py file1.md file2.txt                 # 多个文件
python main.py -i policy.md -o output_dir         # 使用参数
python main.py policy.md --duration 120           # 指定剧本总时长为120秒
python main.py policy.md --no-analysis            # 不保存分析报告
```

## 命令行参数

```
位置参数:
  input_files           输入的政策文件路径（支持多个）

可选参数:
  -h, --help            显示帮助信息
  -i, --input INPUT     输入文件（可多次使用）
  -o, --output-dir DIR  输出目录（默认: output）
  --duration SECONDS   指定剧本总时长（正整数秒，默认: 自动估算）
  --no-analysis         不保存政策分析报告
```

`--duration` 为可选参数，单位为秒，例如 `--duration 60` 表示一分钟。指定后，
叙事设计和详细分镜生成都会按此总时长规划，提示词要求场景时长合计、镜头时长合计
与指定值一致，并根据时长安排台词和动作。未指定时沿用原有逻辑，根据政策内容
自动估算时长（建议30-90秒）。

通过Python调用工作流时，同样可传入 `duration`，省略或传入 `None` 表示自动估算：

```python
from src.workflows.main_workflow import ScriptGenerationWorkflow

workflow = ScriptGenerationWorkflow()
workflow.run(input_files=["policy.md"], duration=60)
```

## 输入文件格式

支持以下格式的政策文档：

- Markdown (`.md`)
- 纯文本 (`.txt`)
- Word文档 (`.docx`)

系统会自动检测文件编码（UTF-8、GBK等）。

### 多政策文档格式

当输入包含多个政策时，系统会自动识别边界：

```markdown
## 一、《政策名称1》
政策内容...

## 二、《政策名称2》
政策内容...
```

或者分别在独立文件中。

## 输出文件

程序会在 `output/` 目录下生成：

1. **剧本文件**：`微短剧剧本_YYYYMMDD_HHMMSS.md`

   - 完整的微短剧剧本，包含角色、场景、镜头、对话等
   - 场景时间说明：
     - **日/夜**：表示场景发生的时间段（白天或夜晚）
     - **内/外**：表示场景地点类型（室内或室外）
     - 示例："日，内"表示白天的室内场景；"夜，外"表示夜晚的室外场景
2. **分析报告**（可选）：`政策分析报告_YYYYMMDD_HHMMSS.md`

   - 政策解析结果，包含政策要点、主体对象、措施等

## 项目结构

```
Script_Gen/
├── main.py                 # 主程序入口
├── run.sh                  # 快速启动脚本
├── requirements.txt        # 依赖列表
├── .env                    # API配置（需自行创建）
├── .env.example            # 配置示例
├── README.md              # 本文件
│
├── src/                   # 源代码
│   ├── models/           # 数据模型和LLM客户端
│   │   ├── schemas.py    # Pydantic数据模型
│   │   ├── llm_client.py # LLM客户端封装
│   │   └── config.py     # 配置管理
│   │
│   ├── parsers/          # 文档解析
│   │   └── policy_parser.py
│   │
│   ├── generators/       # 内容生成
│   │   └── script_generator.py
│   │
│   ├── utils/            # 工具函数
│   │   ├── text_processor.py
│   │   └── output_formatter.py
│   │
│   └── workflows/        # 工作流编排
│       └── main_workflow.py
│
├── prompts/              # 提示词模板
│   ├── policy_analysis.txt
│   ├── policy_synthesis.txt
│   ├── narrative_design.txt
│   └── script_generation.txt
│
└── output/               # 输出目录（自动创建）
```

## 工作流程

1. **文档解析**：读取并解析输入的政策文档
2. **政策分析**：使用LLM深度理解政策内容
3. **政策综合**（多文档时）：整合多个政策的核心信息
4. **叙事设计**：设计适合短视频的叙事框架
5. **剧本生成**：生成详细的微短剧剧本
6. **格式化输出**：生成结构化的Markdown文档

## 技术栈

- **LLM集成**：OpenAI兼容API（支持DeepSeek、OpenAI、vLLM本地部署等）
- **数据验证**：Pydantic v2
- **文档处理**：python-docx, chardet
- **编码检测**：自动检测GBK/UTF-8等编码

## 剧本输出说明

### 场景时间格式

剧本中的场景时间采用影视行业标准格式：

- **日/夜**：场景发生的时间段

  - **日**：白天场景
  - **夜**：夜晚场景
- **内/外**：场景地点类型

  - **内**：室内场景
  - **外**：室外场景

**示例**：

- "日，内"：白天的室内场景（如办公室、家中）
- "夜，外"：夜晚的室外场景（如街道、公园）
- "日，外"：白天的室外场景（如广场、田野）
- "夜，内"：夜晚的室内场景（如餐厅、会议室）

### 剧本结构

生成的剧本包含以下完整要素：

- **剧本题目**：6-12字，贴近日常生活的微短剧风格题目
- **剧本信息**：预估时长、情感基调
- **故事角度**：故事切入点和视角选择
- **叙事结构**：开端、发展、高潮、结局四个部分
- **角色设定**：姓名、类型、描述、外貌服装（2-4个角色）
- **场景设计**：地点、时间、环境描述、预计时长（2-5个场景）
- **完整剧本（分镜脚本）**：按场景组织的详细镜头脚本
  - 镜头类型（特写、中景、全景等）
  - 画面描述
  - 动作描述
  - 对话（含角色、台词、情绪、表演提示）
  - 音效提示
  - 预计时长

## 常见问题

### Q: 如何更换LLM模型？

A: 修改 `.env` 文件中的配置：

**使用在线API服务（如DeepSeek、OpenAI等）**:

```env
OPENAI_API_BASE=https://api.deepseek.com
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=deepseek-chat
```

**使用本地vLLM部署的模型**:

```env
OPENAI_API_BASE=http://localhost:8000/v1
OPENAI_API_KEY=EMPTY
OPENAI_MODEL=your_model_name
```

vLLM部署步骤：

1. 安装vLLM：`pip install vllm`
2. 启动服务：
   ```bash
   python -m vllm.entrypoints.openai.api_server \
       --model /path/to/your/model \
       --host 0.0.0.0 \
       --port 8000
   ```
3. 修改`.env`中的配置指向本地服务
4. 确保模型支持chat格式和function calling（如需结构化输出）

推荐的本地模型：Qwen2.5-14B-Instruct、Llama-3-70B-Instruct等

### Q: 生成的剧本太长或太短怎么办？

A: 使用可选参数指定总时长，例如 `python main.py policy.md --duration 60`。
不指定时，系统仍根据政策内容自动估算时长（建议30-90秒）。

### Q: 支持哪些文件编码？

A: 系统使用 `chardet` 自动检测编码，支持UTF-8、GBK、GB2312等常见中文编码。

### Q: API调用失败怎么办？

A: 系统内置重试机制（最多3次），并使用指数退避策略。如果仍失败，请检查：

- API密钥是否正确
- 网络连接是否正常
- API配额是否充足
