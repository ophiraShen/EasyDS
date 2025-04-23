import os

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据相关路径
DATA_DIR = os.path.join(ROOT_DIR, "data")
DS_DATA_DIR = os.path.join(DATA_DIR, "ds_data")
DS_INDICES_PATH = os.path.join(DS_DATA_DIR, "ds_indices.pkl")
QUESTIONS_DIR = os.path.join(DS_DATA_DIR, "questions")
KNOWLEDGEPOINTS_DIR = os.path.join(DS_DATA_DIR, "knowledgepoints")
ALL_KNOWLEDGEPOINTS_PATH = os.path.join(KNOWLEDGEPOINTS_DIR, "all_knowledgepoints.json")

# 代码相关路径
SRC_DIR = os.path.join(ROOT_DIR, "src")
AGENTS_DIR = os.path.join(SRC_DIR, "agents")
PROMPTS_DIR = os.path.join(AGENTS_DIR, "prompts")
ROUTER_PROMPT_PATH = os.path.join(PROMPTS_DIR, "router_agent_prompt.txt")
TEACHER_PROMPT_PATH = os.path.join(PROMPTS_DIR, "teacher_agent_prompt.txt")
STUDENT_PROMPT_PATH = os.path.join(PROMPTS_DIR, "student_agent_prompt2.txt")
KNOWLEDGE_POINT_SUMMARY_PROMPT_PATH = os.path.join(PROMPTS_DIR, "knowledge_point_summry_promot.txt")

# 模型相关路径
MODELS_DIR = os.path.join(SRC_DIR, "models")
RLHF_DIR = os.path.join(MODELS_DIR, "rlhf")
LORA_PATH = os.path.join(ROOT_DIR, "scripts/rlhf/lora_model")

# Web应用相关路径
WEB_DIR = os.path.join(ROOT_DIR, "web")
STATIC_DIR = os.path.join(WEB_DIR, "static")

# 函数用于保证目录存在
def ensure_dir(dir_path):
    """确保目录存在，如果不存在则创建"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path) 