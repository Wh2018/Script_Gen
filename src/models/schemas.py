"""
数据模型定义
使用Pydantic V2定义所有数据结构
"""
from pydantic import BaseModel, Field
from typing import List


# ===================== 政策解析相关模型 =====================

class PolicyAnalysis(BaseModel):
    """单个政策的分析结果"""
    policy_title: str = Field(description="政策标题")
    policy_summary: str = Field(description="政策摘要（80-120字）")
    background: str = Field(description="政策背景（150-200字）")
    core_goal: str = Field(description="核心目标（80-120字）")
    social_significance: str = Field(description="社会意义（150-200字）")
    policy_subject: List[str] = Field(description="政策主体列表（3-8个）")
    policy_object: List[str] = Field(description="政策对象列表（3-8个）")
    policy_measures: List[str] = Field(description="政策措施列表（5-10条）")
    key_points: List[str] = Field(description="核心要点列表（5-8个，每个15-25字）")


class PolicySynthesis(BaseModel):
    """多个政策的综合分析结果"""
    overall_summary: str = Field(description="综合概述（200-300字）")
    common_themes: List[str] = Field(description="共同主题列表（3-6个）")
    synthesized_key_points: List[str] = Field(description="综合关键要点（6-12个，每个15-30字）")


# ===================== 叙事框架相关模型 =====================

class NarrativeStructure(BaseModel):
    """叙事结构"""
    opening: str = Field(description="开端（80-120字）")
    development: str = Field(description="发展（100-150字）")
    climax: str = Field(description="高潮（80-120字）")
    ending: str = Field(description="结局（80-120字）")


class NarrativeFramework(BaseModel):
    """叙事框架"""
    story_angle: str = Field(description="故事切入角度（100-150字）")
    emotional_tone: str = Field(description="情感基调（50-80字）")
    narrative_structure: NarrativeStructure = Field(description="叙事结构")
    policy_integration_strategy: str = Field(description="政策融入策略（100-150字）")
    estimated_duration: int = Field(
        description="预估时长（整数秒；指定时长时必须等于指定值，未指定时必须>=30）"
    )


# ===================== 剧本生成相关模型 =====================

class Character(BaseModel):
    """角色定义"""
    name: str = Field(description="角色姓名")
    role_type: str = Field(description="角色类型（主角/配角/旁白等）")
    description: str = Field(description="角色描述（100-150字）")
    appearance: str = Field(description="外貌服装描述（80-120字）")


class Scene(BaseModel):
    """场景定义"""
    scene_id: str = Field(description="场景编号（scene_1, scene_2等）")
    location: str = Field(description="地点")
    time_of_day: str = Field(description="时间和场景类型，格式：'日，内'或'夜，外'等。'日/夜'表示白天或夜晚；'内/外'表示室内或室外")
    environment_description: str = Field(description="环境描述（150-250字）")
    estimated_duration: int = Field(description="该场景预计时长（秒）")


class Dialogue(BaseModel):
    """对话"""
    character: str = Field(description="角色名")
    text: str = Field(description="台词内容")
    emotion: str = Field(description="情绪")
    delivery_note: str = Field(description="表演提示", default="")


class Shot(BaseModel):
    """镜头"""
    shot_id: str = Field(description="镜头编号（shot_1, shot_2等）")
    scene_id: str = Field(description="所属场景")
    shot_type: str = Field(description="镜头类型")
    visual_description: str = Field(description="画面描述（150-250字）")
    action_description: str = Field(description="动作描述（80-150字）")
    dialogue: List[Dialogue] = Field(description="对话列表", default_factory=list)
    sound_effects: str = Field(description="音效提示", default="")
    duration_estimate: int = Field(description="该镜头预计时长（秒）")


class ScriptContent(BaseModel):
    """完整剧本内容"""
    title: str = Field(description="剧本题目（6-12字，贴近日常生活，符合微短剧命名风格，避免官方政策话术）")
    characters: List[Character] = Field(description="角色列表（2-4个）")
    scenes: List[Scene] = Field(
        description="场景列表（未指定时长时2-5个；指定时长时按实际时长调整）"
    )
    shots: List[Shot] = Field(description="镜头列表")
