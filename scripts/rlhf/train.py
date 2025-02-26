# EasyDS/scripts/rlhf/train.py
import os
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    DataCollatorForSeq2Seq, 
    HfArgumentParser,
    TrainingArguments, 
    Trainer,
    set_seed,
    get_scheduler
)
from peft import LoraConfig, TaskType, get_peft_model
from accelerate import Accelerator
from accelerate.utils import DeepSpeedPlugin
from tqdm import tqdm

from utils import empty_cache
from data_preprocess import InputOutputDataset, prepare_dataloaders
from arguments import ModelArguments, DataTrainingArguments, PeftArguments


def setup_model_and_tokenizer(model_args):
    """设置模型和分词器"""
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        model_args.model_name_or_path,
        truncation=True,
        max_length=786,
        trust_remote_code=True
    )
    
    return model, tokenizer

def setup_lora(model, peft_args):
    """设置LoRA"""
    if peft_args.target_modules:
        peft_args.target_modules = peft_args.target_modules.split(",")
    else:
        peft_args.target_modules = ["q_proj", "k_proj", "v_proj"]
    
    lora_config = LoraConfig(
        inference_mode=False,
        task_type=TaskType.CAUSAL_LM,
        target_modules=peft_args.target_modules,
        r=peft_args.lora_rank,
        lora_alpha=peft_args.lora_alpha,
        lora_dropout=peft_args.lora_dropout
    )
    
    return get_peft_model(model, lora_config)

def save_model_state(model, accelerator, save_path, is_final_save=False, training_state=None):
    """保存模型状态"""
    # 确保所有进程同步
    if is_final_save:
        accelerator.wait_for_everyone()
    
    # 在主进程中创建目录
    if accelerator.is_main_process:
        os.makedirs(save_path, exist_ok=True)
    
    # 等待目录创建完成
    accelerator.wait_for_everyone()
    
    # 主进程保存模型
    if accelerator.is_main_process:
        unwrapped_model = accelerator.unwrap_model(model)
        unwrapped_model.save_pretrained(
            save_path,
            is_main_process=accelerator.is_main_process,
            save_function=accelerator.save,
            save_peft=True,
            save_model_only=True  
        )
    
    # 保存训练状态
    if training_state is not None:
        # 确保训练状态目录存在
        if accelerator.is_main_process:
            os.makedirs(save_path, exist_ok=True)
        accelerator.wait_for_everyone()
        
        # 使用 accelerator 的保存函数
        accelerator.save(training_state, f"{save_path}/training_state.pt")
    

def main():
    # 1. 解析参数
    parser = HfArgumentParser((ModelArguments, DataTrainingArguments, PeftArguments, TrainingArguments))
    model_args, data_args, peft_args, training_args = parser.parse_args_into_dataclasses()
    
    # 2. 初始化系统环境
    # 设置随机种子
    set_seed(training_args.seed)
    
    # 初始化 DeepSpeed 和 Accelerator
    deepspeed_plugin = DeepSpeedPlugin(
        zero_stage=3,
        gradient_accumulation_steps=training_args.gradient_accumulation_steps
    )
    accelerator = Accelerator(
        gradient_accumulation_steps=training_args.gradient_accumulation_steps,
        deepspeed_plugin=deepspeed_plugin,
        mixed_precision="bf16"
    )
    
    # 3. 模型初始化
    # 加载模型和分词器
    model, tokenizer = setup_model_and_tokenizer(model_args)
    model = setup_lora(model, peft_args)
    model.print_trainable_parameters()
    
    # 4. 数据准备
    # 准备数据加载器
    train_dataloader, eval_dataloader = prepare_dataloaders(
        data_args, tokenizer, training_args
    )
    
    # 5. 训练配置
    # 优化器设置
    optimizer = torch.optim.Adam(model.parameters(), lr=training_args.learning_rate)
    lr_scheduler = torch.optim.lr_scheduler.LinearLR(optimizer)
    
    # 使用 Accelerator 准备所有组件
    model, optimizer, train_dataloader, eval_dataloader, lr_scheduler = accelerator.prepare(
        model, optimizer, train_dataloader, eval_dataloader, lr_scheduler
    )
    
    
    # 6. 训练循环
    if training_args.do_train:
        model.train()
        total_steps = len(train_dataloader) * training_args.num_train_epochs
        progress_bar = tqdm(range(int(total_steps)), desc="Training")
        
        for epoch in range(int(training_args.num_train_epochs)):
            for step, batch in enumerate(train_dataloader):
                outputs = model(**batch)
                loss = outputs.loss
                accelerator.backward(loss)
                
                if step % training_args.gradient_accumulation_steps == 0:
                    optimizer.step()
                    lr_scheduler.step()
                    optimizer.zero_grad()
                    empty_cache()
                
                
                if training_args.logging_steps > 0 and step % training_args.logging_steps == 0:
                    accelerator.print(f"Epoch {epoch}, Step {step}, Loss: {loss.item():.4f}")

                # 保存checkpoint
                if step % training_args.save_steps == 0:
                    save_model_state(
                        model,
                        accelerator,
                        f"{training_args.output_dir}/checkpoint-{step}",
                        training_state={
                            "epoch": epoch,
                            "step": step,
                            "optimizer_state": optimizer.state_dict(),
                            "lr_scheduler_state": lr_scheduler.state_dict(),
                        }
                    )

                progress_bar.update(1)
    
    # 7. 模型评估
    if training_args.do_eval:
        model.eval()
        eval_loss = 0
        eval_steps = 0
        
        for batch in eval_dataloader:
            with torch.no_grad():
                outputs = model(**batch)
                eval_loss += outputs.loss.item()
                eval_steps += 1
        
        eval_loss /= eval_steps
        accelerator.print(f"Eval Loss: {eval_loss:.4f}")
    
    # 8. 保存模型
    if training_args.output_dir:
        save_model_state(
            model,
            accelerator,
            training_args.output_dir,
            is_final_save=True
        )

if __name__ == "__main__":
    main()