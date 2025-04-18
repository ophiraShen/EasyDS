import os
from pydantic import BaseModel

class Settings(BaseModel):
    """应用配置"""
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "EasyDS"
    
    # 路径配置
    BASE_DIR: str = "/root/autodl-tmp/EasyDS"
    DATA_DIR: str = os.path.join(BASE_DIR, "data/ds_data")
    
    # 知识索引配置
    INDICES_PATH: str = os.path.join(DATA_DIR, "ds_indices.pkl")

settings = Settings() 