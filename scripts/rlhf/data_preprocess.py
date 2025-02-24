# EasyDS/scripts/rlhf/data_preprocess.py
import json
from typing import List, Dict, Any
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import DataCollatorForSeq2Seq


# 定义一个名为 InputOutputDataset 的新类，它继承自 Dataset 类。这使得我们的数据集能够与 PyTorch 的数据加载器兼容，支持批处理和其他数据加载功能
class InputOutputDataset(Dataset):
    # 定义类的初始化方法，接收三个参数：data（数据集）、tokenizer（分词器）、args（其他参数配置）
    def __init__(self, data, tokenizer, args):
        # 调用父类 Dataset 的初始化方法，以确保数据集正确初始化。这是继承类的标准做法
        super(InputOutputDataset, self).__init__()
        self.data = data
        self.tokenizer = tokenizer
        self.prompt_column = args.prompt_column
        self.response_column = args.response_column
        self.max_source_length = args.max_source_length
        self.max_target_length = args.max_target_length

    # 用于返回数据集的长度，满足 Python 的长度协议
    def __len__(self):
        return len(self.data)

    # 通过索引访问数据集中的样本
    def __getitem__(self, i):
        item = self.data[i]
        
        # 1. 对输入文本进行编码
        context = self.tokenizer(
            build_prompt(item[self.prompt_column]), 
            max_length=self.max_source_length, 
            add_special_tokens=False)
        
        # 2. 对输出文本进行编码
        response = self.tokenizer(
            build_response(item[self.response_column]), 
            max_length=self.max_target_length, 
            add_special_tokens=False)
        
        # 3. 构建训练所需的数据格式
        # 将上下文和响应的 input_ids 连接起来，形成一个完整的输入序列
        input_ids = context["input_ids"] + response["input_ids"]
        # 将上下文和响应的注意力掩码连接起来，确保模型在计算注意力时能够正确地关注输入序列的相关部分
        attention_mask = context["attention_mask"] + response["attention_mask"]
        # 创建标签数组，标记上下文部分为 -100（表示在计算损失时忽略），而响应部分使用真实的 input_ids
        labels = [-100] * len(context["input_ids"]) + response["input_ids"]
        # 确保输入 ID 和标签的长度一致，如果不一致，将抛出断言错误，提供长度信息以便调试
        assert len(input_ids) == len(labels), f"length mismatch: {len(input_ids)} vs {len(labels)}"
        # 返回一个字典，其中包含编码后的输入 ID、注意力掩码和标签，供模型训练使用
        return {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": labels
        }

# 用于构建提示字符串
def build_prompt(context):
    # 检查上下文是否为字符串类型，如果是，则将其解析为 JSON 对象
    if isinstance(context,str):
        context = json.loads(context)
    # 初始化一个空字符串，用于存储构建的提示文本
    prompt = ''
    # 遍历上下文中的每个对话轮次
    for turn in context:
        # 检查角色是否为系统、用户或助手
        if turn["role"] == "system":
            prompt += f'<|system|>\n{turn["content"]}<|endoftext|>\n'
        elif turn["role"] == "user":
            prompt += f'<|user|>\n{turn["content"]}<|endoftext|>\n'
        elif turn["role"] == "assistant":
            prompt += f'<|assistant|>\n{turn["content"]}<|endoftext|>\n'
        
    # 返回构建好的完整提示字符串
    return prompt

# 用于构建响应字符串
def build_response(response):
    # 检查响应是否为字符串类型，若是则解析为 JSON 对象
    if isinstance(response,str):
        response = json.loads(response)
    # 判断角色是否为助手
    if response["role"] == "assistant":
        # 构建助手的响应字符串，格式为
        return '<sop>assistant\n' + response["content"] + '<eop>'
    return ''


def load_data(file_path: str) -> List[Dict[str, Any]]:
    """
    加载JSONL格式的数据文件
    Args:
        file_path: 数据文件路径
    Returns:
        List[Dict]: 数据列表
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            data.append(json.loads(line))
    return data


def prepare_dataloaders(data_args, tokenizer, training_args):
    """
    准备数据加载器
    Args:
        data_args: 数据相关参数
        tokenizer: 分词器
        training_args: 训练相关参数
    Returns:
        tuple: (训练数据加载器, 评估数据加载器)
    """
    # 数据整理器
    data_collator = DataCollatorForSeq2Seq(
        tokenizer=tokenizer,
        padding=True,
        pad_to_multiple_of=8
    )
    
    # 加载训练数据
    train_data = None
    if training_args.do_train:
        train_data = load_data(data_args.train_file)
        train_dataset = InputOutputDataset(train_data, tokenizer, data_args)
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=training_args.per_device_train_batch_size,
            collate_fn=data_collator,
            shuffle=True,
            num_workers=8,
            pin_memory=True
        )
    
    # 加载评估数据
    eval_data = None
    if training_args.do_eval:
        eval_data = load_data(data_args.validation_file)
        eval_dataset = InputOutputDataset(eval_data, tokenizer, data_args)
        eval_dataloader = DataLoader(
            eval_dataset,
            batch_size=training_args.per_device_eval_batch_size,
            collate_fn=data_collator
        )
    
    return train_dataloader if train_data else None, eval_dataloader if eval_data else None