import os
import re
import json
def combine_text_files(file_paths):
    """合并多个文本文件的内容"""
    combined_text = ""
    for file_path in file_paths:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                combined_text += f.read() + "\n"
    return combined_text

def extract_choice_questions(text):
    """提取选择题部分"""
    # 找到"一、单项选择题"的位置
    start_index = text.find("一、单项选择题")
    if start_index == -1:
        return ""
    
    # 从这个位置开始查找"二、"
    text_after_start = text[start_index:]
    end_index = text_after_start.find("二、")
    
    if end_index != -1:  # 找到了"二、"
        return text_after_start[:end_index]
    else:
        return text_after_start

def parse_questions(questions_text):
    """解析题目内容"""
    questions = {}
    current_question = []
    current_number = None
    
    # 跳过"一、单项选择题"之前的内容
    content = questions_text.split("一、单项选择题", 1)[1]
    
    for line in content.split('\n'):
        # 匹配题号（形如 01. 02. 等）
        match = re.match(r'^(\d{2})\.\s*(.+)', line)
        if match:
            # 保存前一个题目
            if current_number:
                questions[current_number] = '\n'.join(filter(None, current_question))
            # 开始新题目
            current_number = match.group(1)
            current_question = [match.group(2)]
        elif current_number and line.strip():
            current_question.append(line.strip())
    
    # 保存最后一个题目
    if current_number:
        questions[current_number] = '\n'.join(filter(None, current_question))
    
    return questions

def parse_answers(answers_text):
    """解析答案内容"""
    answers = {}
    current_number = None
    current_answer = None
    current_explanation = []
    
    # 跳过"一、单项选择题"之前的内容
    content = answers_text.split("一、单项选择题", 1)[1]
    
    for line in content.split('\n'):
        # 匹配答案（形如 01.B 或 01. B）
        match = re.match(r'^(\d{2})\.\s*([A-D])\s*$', line)
        if match:
            # 保存前一题的内容
            if current_number:
                answers[current_number] = {
                    "答案": current_answer,
                    "解析": '\n'.join(filter(None, current_explanation))
                }
            # 开始新题目
            current_number = match.group(1)
            current_answer = match.group(2)
            current_explanation = []
        elif current_number and line.strip():
            current_explanation.append(line.strip())
    
    # 保存最后一题的内容
    if current_number:
        answers[current_number] = {
            "答案": current_answer,
            "解析": '\n'.join(filter(None, current_explanation))
        }
    
    return answers

def process_questions_and_answers(question_files, answer_files):
    """处理题目和答案文件"""
    # 合并题目文件
    questions_text = combine_text_files(question_files)
    questions_section = extract_choice_questions(questions_text)
    questions = parse_questions(questions_section)
    
    # 合并答案文件
    answers_text = combine_text_files(answer_files)
    answers_section = extract_choice_questions(answers_text)
    answers = parse_answers(answers_section)
    
    # 合并题目和答案
    result = []
    for number in sorted(questions.keys()):
        if number.isdigit() and 1 <= int(number) <= 36:
            answer_info = answers.get(number, {"答案": "未找到", "解析": "未找到解析"})
            item = {
                "题号": number,
                "题目": questions[number].strip(),
                "答案": answer_info["答案"],
                "解析": answer_info["解析"]
            }
            result.append(item)
    
    return result

question_files = []
answer_files = []

file = "/root/autodl-tmp/EasyDS/data/DS2026_extracted/text"
id = "q0210"
for i in range(25,26):
    question_files.append(os.path.join(file,f"page_{i}.txt"))
for i in range(26,27):
    answer_files.append(os.path.join(file,f"page_{i}.txt"))

results = process_questions_and_answers(question_files, answer_files)

questions = []
for q in results:
    question = {
  "id": id+q["题号"],            # 问题唯一标识符
  "title": "title",         # 问题标题
  "content": q["题目"],       # 问题内容
  "difficulty": "integer",   # 难度等级 (1-5)
  "type": "concept",          # 问题类型 ("concept", "calculation", "application")
  "knowledge_points": [      # 相关知识点ID列表
    "kc0111"
  ],
  "related_questions": [     # 相关问题（用于扩展）
    {
      "id": "string",        # 相关问题ID
      "relation_type": "string" # 关系类型: "extension", "application", "contrast"
    }
  ],
  "reference_answer": {      # 参考答案
    "content": q["答案"],     # 答案内容
    "key_points": [          # 关键点列表
      "string"
    ],
    "explanation": q["解析"]   # 详细解释
  }
}
    questions.append(question)

with open("/root/autodl-tmp/EasyDS/data/ds_data/questions/chapter_2.json","r",encoding="utf-8") as f:
    data = json.load(f)

data += questions

with open("/root/autodl-tmp/EasyDS/data/ds_data/questions/chapter_2.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=4)
