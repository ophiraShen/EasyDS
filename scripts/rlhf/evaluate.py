# EasyDS/scripts/rlhf/evaluate.py
import json
import torch
import argparse
from tqdm import tqdm
from peft import PeftModel
from transformers import AutoTokenizer, AutoModelForCausalLM
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_model(model_path, checkpoint_path):
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        trust_remote_code=True,
        torch_dtype=torch.float16
    )
    model = PeftModel.from_pretrained(model, checkpoint_path).to("cuda").eval()
    return tokenizer, model

class Evaluator:
    def __init__(self, tokenizer, model, data_path):
        self.tokenizer = tokenizer
        self.model = model
        self.data_path = data_path
        self.smooth = SmoothingFunction().method3

    def calculate_prf(self, pred, label):
        """计算Precision, Recall, F1分数"""
        pred_tokens = set(list(pred.strip()))
        label_tokens = set(list(label.strip()))
        
        if not pred_tokens or not label_tokens:
            return 0, 0, 0

        # 计算交集
        common = pred_tokens.intersection(label_tokens)
        
        # 计算precision, recall, f1
        precision = len(common) / len(pred_tokens) if pred_tokens else 0
        recall = len(common) / len(label_tokens) if label_tokens else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0
        
        return precision, recall, f1

    def calculate_bleu(self, pred, label):
        """计算BLEU分数"""
        try:
            pred_chars = list(pred.strip())
            label_chars = list(label.strip())
            
            if len(pred_chars) == 0 or len(label_chars) == 0:
                return 0
                
            return sentence_bleu(
                [label_chars], 
                pred_chars, 
                smoothing_function=self.smooth
            )
        except Exception as e:
            logger.warning(f"Error calculating BLEU: {str(e)}")
            return 0

    def generate_response(self, input_text):
        """生成模型响应"""
        try:
            inputs = self.tokenizer(input_text, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=256,
                    num_beams=1,  # 使用贪婪搜索提高速度
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return ""

    def compute_metrics(self):
        """计算评估指标"""
        metrics = {
            "bleu-4": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "f1": 0.0,
            "samples": 0
        }
        results = []

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                test_dataset = [json.loads(line) for line in f]

            for item in tqdm(test_dataset, desc="Evaluating"):
                input_text = item["input"]
                reference = item["output"]

                # 生成响应
                prediction = self.generate_response(input_text)
                
                # 计算BLEU分数
                bleu_score = self.calculate_bleu(prediction, reference)
                
                # 计算PRF分数
                precision, recall, f1 = self.calculate_prf(prediction, reference)

                # 累加分数
                metrics["bleu-4"] += bleu_score
                metrics["precision"] += precision
                metrics["recall"] += recall
                metrics["f1"] += f1
                metrics["samples"] += 1

                # 保存样本结果
                if metrics["samples"] % 10 == 0:
                    results.append({
                        "input": input_text,
                        "reference": reference,
                        "prediction": prediction,
                        "metrics": {
                            "bleu-4": bleu_score,
                            "precision": precision,
                            "recall": recall,
                            "f1": f1
                        }
                    })
                    # 输出中间结果
                    interim_metrics = {k: round((v/metrics["samples"])*100, 4) 
                                    for k, v in metrics.items() if k != "samples"}
                    logger.info(f"Processed {metrics['samples']}/{len(test_dataset)}: {interim_metrics}")

            # 计算平均分数
            final_metrics = {}
            for key in metrics:
                if key != "samples":
                    final_metrics[key] = round((metrics[key] / metrics["samples"]) * 100, 4)
            final_metrics["samples"] = metrics["samples"]
            
            logger.info(f"Final Evaluation Results: {final_metrics}")

            # 保存详细结果
            output_file = "evaluation_results.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump({
                    "metrics": final_metrics,
                    "results": results
                }, f, ensure_ascii=False, indent=2)
            
            return final_metrics

        except Exception as e:
            logger.error(f"Error in evaluation: {str(e)}")
            return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, required=True,
                       help="Base model path")
    parser.add_argument("--ckpt", type=str, required=True,
                       help="LoRA checkpoint path")
    parser.add_argument("--data", type=str, required=True,
                       help="Test dataset path (JSONL format)")
    args = parser.parse_args()

    try:
        tokenizer, model = load_model(args.model, args.ckpt)
        evaluator = Evaluator(tokenizer, model, args.data)
        evaluator.compute_metrics()
    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")

if __name__ == "__main__":
    main()