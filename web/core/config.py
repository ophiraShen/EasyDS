import os
from pydantic import BaseModel

# 获取项目根目录的绝对路径
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseModel):
    """应用配置"""
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "EasyDS"
    
    # 路径配置
    BASE_DIR: str = ROOT_DIR
    DATA_DIR: str = os.path.join(BASE_DIR, "data/ds_data")
    
    # 知识索引配置
    INDICES_PATH: str = os.path.join(DATA_DIR, "ds_indices.pkl")

settings = Settings() 