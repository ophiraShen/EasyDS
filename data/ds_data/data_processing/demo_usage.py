#!/usr/bin/env python
# -*- coding: utf-8 -*-

from index_builder import KnowledgeIndexSystem

def main():
    """演示知识点索引系统的使用方法"""
    print("加载索引系统...")
    
    # 方法1：重新构建索引
    # system = KnowledgeIndexSystem()
    # system.build_indices()
    # system.save_indices('ds_indices.pkl')
    
    # 方法2：从文件加载已构建好的索引（推荐，更快）
    try:
        system = KnowledgeIndexSystem.load_indices('/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl')
        print("成功从文件加载索引")
    except FileNotFoundError:
        print("未找到索引文件，正在重新构建...")
        system = KnowledgeIndexSystem()
        system.build_indices()
        system.save_indices('ds_indices.pkl')
    
    while True:
        print("\n" + "="*50)
        print("知识点查询系统")
        print("1. 通过知识点ID查询知识点")
        print("2. 查询知识点对应的题目")
        print("3. 通过题目ID查询题目")
        print("0. 退出")
        
        choice = input("请输入选项（0-3）: ")
        
        if choice == '0':
            print("感谢使用！")
            break
        
        elif choice == '1':
            kp_id = input("请输入知识点ID (例如 kc0111): ")
            kp = system.get_knowledge_point(kp_id)
            
            if kp:
                print(f"\n知识点 {kp_id}: {kp['title']}")
                print(f"所属章节: {kp['chapter_id']}")
                print(f"描述: {kp['description'][:100]}...")  # 只显示前100个字符
            else:
                print(f"未找到知识点 {kp_id}")
        
        elif choice == '2':
            kp_id = input("请输入知识点ID (例如 kc0111): ")
            questions = system.get_questions_by_knowledge(kp_id)
            
            if questions:
                print(f"\n知识点 {kp_id} 下有 {len(questions)} 个题目:")
                for i, q in enumerate(questions[:5], 1):  # 只显示前5个
                    print(f"{i}. 题目ID: {q['id']}, 标题: {q['title']}")
                
                if len(questions) > 5:
                    print(f"... 还有 {len(questions) - 5} 个题目未显示")
                
                # 询问是否查看具体题目
                if input("\n是否查看某个题目详情？(y/n): ").lower() == 'y':
                    idx = int(input(f"请输入题目序号(1-{min(len(questions), 5)}): "))
                    if 1 <= idx <= min(len(questions), 5):
                        q = questions[idx-1]
                        print(f"\n题目ID: {q['id']}")
                        print(f"标题: {q['title']}")
                        print(f"内容: {q['content']}")
                        print(f"参考答案: {q.get('reference_answer', {}).get('content', '未提供')}")
                        print(f"解析: {q.get('reference_answer', {}).get('explanation', '未提供')[:200]}...")
            else:
                print(f"知识点 {kp_id} 下没有题目")
        
        elif choice == '3':
            q_id = input("请输入题目ID (例如 q011002): ")
            question = system.get_question(q_id)
            
            if question:
                print(f"\n题目ID: {question['id']}")
                print(f"标题: {question['title']}")
                print(f"内容: {question['content']}")
                print(f"知识点: {', '.join(question.get('knowledge_points', []))}")
                print(f"参考答案: {question.get('reference_answer', {}).get('content', '未提供')}")
                print(f"解析: {question.get('reference_answer', {}).get('explanation', '未提供')[:200]}...")
            else:
                print(f"未找到题目 {q_id}")
        
        else:
            print("无效选项，请重新输入")

if __name__ == "__main__":
    main() 