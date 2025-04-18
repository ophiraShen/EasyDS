# src/demo.py
import os
import sys
import asyncio
from typing import Dict, List
import json

sys.path.append("/root/autodl-tmp/EasyDS")
from src.knowledge_qa_system import KnowledgeQASystem

async def display_chapters(qa_system: KnowledgeQASystem):
    """显示所有章节"""
    chapters = qa_system.get_chapters()
    print("\n==== 章节列表 ====")
    for i, chapter in enumerate(chapters, 1):
        print(f"{i}. {chapter['title']}")
    return chapters

async def display_questions(qa_system: KnowledgeQASystem, chapter_id: str):
    """显示章节内的问题"""
    questions = qa_system.get_questions_by_chapter(chapter_id)
    print(f"\n==== 第{chapter_id}章问题列表 ====")
    for i, q in enumerate(questions[:10], 1):  # 只显示前10个问题
        print(f"{i}. {q['title']}")
    return questions[:10]

async def display_question_detail(qa_system: KnowledgeQASystem, question_id: str):
    """显示问题详情"""
    question = qa_system.get_question_detail(question_id)
    if not question:
        print(f"找不到问题: {question_id}")
        return None
    
    print(f"\n==== 问题详情 ====")
    print(f"标题: {question['title']}")
    print(f"内容: {question['content']}")
    
    if 'options' in question and question['options']:
        print("\n选项:")
        for key, value in question['options'].items():
            print(f"{key}. {value}")
    
    return question

async def interactive_session(qa_system: KnowledgeQASystem, question_id: str):
    """交互式问答会话"""
    # 创建会话
    session_id = qa_system.create_session(question_id)
    print(f"\n会话已创建 (ID: {session_id})")
    
    # 开始问答
    print("\n==== 开始问答 ====")
    print("输入你的答案(输入'q'退出):")
    
    while True:
        user_input = input("\n> ")
        if user_input.lower() == 'q':
            break
        
        print("\nAI回复中...")
        # 使用流式输出
        async for chunk, node in qa_system.process_answer(session_id, user_input):
            if node == "student_agent":
                print(chunk, end="", flush=True)
            elif node == "teacher_agent":
                print(chunk, end="", flush=True)
        print()  # 打印换行
        
        # 询问用户是否继续
        cont = input("\n继续对话? (y/n): ")
        if cont.lower() != 'y':
            break
            
    # 显示相关知识点
    knowledge_points = qa_system.get_related_knowledge_points(question_id)
    if knowledge_points:
        print("\n==== 相关知识点 ====")
        for kp in knowledge_points:
            print(f"- {kp['title']}: {kp['summry']}")
    
    # 显示相似问题
    similar_questions = qa_system.get_similar_questions(question_id)
    if similar_questions:
        print("\n==== 相似问题 ====")
        for i, q in enumerate(similar_questions, 1):
            print(f"{i}. {q['title']} (ID: {q['id']})")

async def main():
    """主函数"""
    qa_system = KnowledgeQASystem()
    
    while True:
        # 显示章节列表
        chapters = await display_chapters(qa_system)
        
        # 选择章节
        chapter_idx = input("\n选择章节 (1-8,q退出): ")
        if chapter_idx.lower() == 'q':
            break
            
        if not chapter_idx.isdigit() or int(chapter_idx) < 1 or int(chapter_idx) > len(chapters):
            print("无效选择")
            continue
        
        chapter = chapters[int(chapter_idx) - 1]
        
        # 显示问题列表
        questions = await display_questions(qa_system, chapter['id'])
        
        # 选择问题
        question_idx = input("\n选择问题 (1-10,b返回,q退出): ")
        if question_idx.lower() == 'q':
            break
        if question_idx.lower() == 'b':
            continue
            
        if not question_idx.isdigit() or int(question_idx) < 1 or int(question_idx) > len(questions):
            print("无效选择")
            continue
        
        question = questions[int(question_idx) - 1]
        
        # 显示问题详情
        await display_question_detail(qa_system, question['id'])
        
        # 开始交互式会话
        await interactive_session(qa_system, question['id'])
        
        # 询问是否继续
        cont = input("\n继续做题? (y/n): ")
        if cont.lower() != 'y':
            break

if __name__ == "__main__":
    asyncio.run(main())