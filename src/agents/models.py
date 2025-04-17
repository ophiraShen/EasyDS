# src/agents/models.py
import os

from typing import Optional, Union, Any
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

class BaseModelWrapper:
    """基础模型包装类"""
    def __init__(self, model_name: str = "deepseek-chat", api_key: Optional[str] = None, **kwargs):
        self.model_name = model_name
        self.api_key = api_key
        self.kwargs = kwargs
        self.model = self._init_model()
    
    def _init_model(self) -> BaseChatModel:
        raise NotImplementedError

class DeepseekWrapper(BaseModelWrapper):
    """Deepseek 模型包装类"""
    def _init_model(self) -> BaseChatModel:
        return ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key or os.getenv("DEEPSEEK_API_KEY"),
            openai_api_base='https://api.deepseek.com',
            temperature=0.9,
            max_tokens=1000,
            **self.kwargs
        )

def get_llm(model_type: str = "deepseek", **kwargs) -> BaseChatModel:
    """获取 LLM 模型实例"""
    model_map = {
        "deepseek": DeepseekWrapper,
        # 这里可以添加其他模型的包装类
    }
    
    wrapper_cls = model_map.get(model_type)
    if not wrapper_cls:
        raise ValueError(f"Unsupported model type: {model_type}")
        
    return wrapper_cls(**kwargs).model