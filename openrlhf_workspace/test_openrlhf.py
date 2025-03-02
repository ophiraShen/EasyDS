import openrlhf
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"GPU name: {torch.cuda.get_device_name(0)}")

# 测试 OpenRLHF 的基本功能
from openrlhf.models import Actor, RewardModel
print("Testing model loading...")
try:
    # 尝试加载一个小模型进行测试
    model = Actor.from_pretrained("/root/autodl-fs/modelscope/glm_4_9b_chat", device_map="auto")
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")
