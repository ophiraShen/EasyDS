import json
import os
import pickle
import asyncio
from typing import Dict, List, Any, Optional

class KnowledgeIndexSystem:
    """知识点索引系统，用于快速查找知识点和相关题目"""
    
    def __init__(self, data_dir: str = '../'):
        """初始化索引系统
        
        Args:
            data_dir: 数据目录路径，默认为上级目录
        """
        self.data_dir = data_dir
        # 知识点索引: {knowledge_id: knowledge_point_object}
        self.knowledge_index: Dict[str, dict] = {}
        # 知识点对应题目索引: {knowledge_id: [question_ids]}
        self.knowledge_question_index: Dict[str, List[str]] = {}
        # 题目索引: {question_id: question_object}
        self.question_index: Dict[str, dict] = {}
        # 章节索引: {chapter_id: chapter_object}
        self.chapter_index: Dict[str, dict] = {}
        
    def build_indices(self):
        """构建所有索引"""
        self._load_chapters()
        self._load_knowledge_points()
        self._load_questions()
        print("索引构建完成!")
        
    def _load_chapters(self):
        """加载章节信息"""
        chapters_path = os.path.join(self.data_dir, 'chapters.json')
        if os.path.exists(chapters_path):
            with open(chapters_path, 'r', encoding='utf-8') as f:
                chapters = json.load(f)
                for chapter in chapters:
                    self.chapter_index[chapter['id']] = chapter
            print(f"加载了 {len(self.chapter_index)} 个章节")
    
    def _load_knowledge_points(self):
        """加载所有知识点"""
        # 可以加载单个综合文件或分章节的文件
        kp_dir = os.path.join(self.data_dir, 'knowledgepoints')
        
        # 尝试加载综合文件
        all_kp_path = os.path.join(kp_dir, 'all_knowledgepoints.json')
        if os.path.exists(all_kp_path):
            with open(all_kp_path, 'r', encoding='utf-8') as f:
                knowledge_points = json.load(f)
                for kp in knowledge_points:
                    self.knowledge_index[kp['id']] = kp
                    # 初始化该知识点的题目列表
                    if 'questions' in kp:
                        self.knowledge_question_index[kp['id']] = kp['questions']
                    else:
                        self.knowledge_question_index[kp['id']] = []
            print(f"从全量文件加载了 {len(self.knowledge_index)} 个知识点")
            return
        
        # 如果没有综合文件，则加载各章节的知识点文件
        for chapter_num in range(1, 9):  # 假设有8个章节
            chapter_file = os.path.join(kp_dir, f'chapter_{chapter_num}.json')
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    knowledge_points = json.load(f)
                    for kp in knowledge_points:
                        self.knowledge_index[kp['id']] = kp
                        # 初始化该知识点的题目列表
                        if 'questions' in kp:
                            self.knowledge_question_index[kp['id']] = kp['questions']
                        else:
                            self.knowledge_question_index[kp['id']] = []
                print(f"从章节{chapter_num}加载了 {len(knowledge_points)} 个知识点")
    
    def _load_questions(self):
        """加载所有题目"""
        q_dir = os.path.join(self.data_dir, 'questions')
        
        # 加载各章节的题目
        for chapter_num in range(1, 9):  # 假设有8个章节
            chapter_file = os.path.join(q_dir, f'chapter_{chapter_num}.json')
            if os.path.exists(chapter_file):
                with open(chapter_file, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                    for q in questions:
                        # 将题目添加到题目索引
                        self.question_index[q['id']] = q
                        
                        # 将题目ID添加到对应知识点的题目列表中
                        if 'knowledge_points' in q:
                            for kp_id in q['knowledge_points']:
                                if kp_id not in self.knowledge_question_index:
                                    self.knowledge_question_index[kp_id] = []
                                if q['id'] not in self.knowledge_question_index[kp_id]:
                                    self.knowledge_question_index[kp_id].append(q['id'])
                print(f"从章节{chapter_num}加载了 {len(questions)} 个题目")

    def get_chapter_list(self) -> List[Dict]:
        """获取所有章节的列表
        
        Returns:
            章节列表，每个章节包含id和title
        """
        chapters = []
        for chapter_id, chapter in self.chapter_index.items():
            chapters.append({
                "id": chapter_id,
                "title": chapter.get("title", f"第{chapter_id}章")
            })
        # 按章节ID排序
        chapters.sort(key=lambda x: x["id"])
        return chapters
    
    def get_questions_by_chapter(self, chapter_id: str) -> List[Dict]:
        """获取指定章节的所有题目
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            题目列表
        """
        # 找出以该章节ID开头的所有题目
        questions = []
        prefix = f"q{chapter_id}"
        
        for question_id, question in self.question_index.items():
            if question_id.startswith(prefix):
                questions.append({
                    "id": question_id,
                    "title": question.get("title", ""),
                    "type": question.get("type", "选择题"),
                    "difficulty": question.get("difficulty", "中等")
                })
        
        return questions
    
    def get_knowledge_point(self, knowledge_id: str) -> Optional[dict]:
        """根据知识点ID获取知识点信息
        
        Args:
            knowledge_id: 知识点ID，例如 "kc0111"
            
        Returns:
            知识点对象，如果不存在则返回None
        """
        return self.knowledge_index.get(knowledge_id)
    
    async def get_knowledge_point_async(self, knowledge_id: str) -> Optional[dict]:
        """异步方式根据知识点ID获取知识点信息
        
        Args:
            knowledge_id: 知识点ID，例如 "kc0111"
            
        Returns:
            知识点对象，如果不存在则返回None
        """
        # 这里实际上不需要IO操作，但为了保持API一致性提供异步版本
        return self.knowledge_index.get(knowledge_id)
    
    def get_questions_by_knowledge(self, knowledge_id: str) -> List[dict]:
        """根据知识点ID获取相关题目列表
        
        Args:
            knowledge_id: 知识点ID，例如 "kc0111"
            
        Returns:
            题目对象列表
        """
        question_ids = self.knowledge_question_index.get(knowledge_id, [])
        return [self.question_index[qid] for qid in question_ids if qid in self.question_index]
    
    async def get_questions_by_knowledge_async(self, knowledge_id: str) -> List[dict]:
        """异步方式根据知识点ID获取相关题目列表
        
        Args:
            knowledge_id: 知识点ID，例如 "kc0111"
            
        Returns:
            题目对象列表
        """
        question_ids = self.knowledge_question_index.get(knowledge_id, [])
        return [self.question_index[qid] for qid in question_ids if qid in self.question_index]
    
    def get_question(self, question_id: str) -> Optional[dict]:
        """根据题目ID获取题目信息
        
        Args:
            question_id: 题目ID，例如 "q011002"
            
        Returns:
            题目对象，如果不存在则返回None
        """
        return self.question_index.get(question_id)
    
    async def get_question_async(self, question_id: str) -> Optional[dict]:
        """异步方式根据题目ID获取题目信息
        
        Args:
            question_id: 题目ID，例如 "q011002"
            
        Returns:
            题目对象，如果不存在则返回None
        """
        return self.question_index.get(question_id)
    
    def save_indices(self, output_path: str = 'indices.pkl'):
        """将构建的索引保存到文件中
        
        Args:
            output_path: 输出文件路径
        """
        indices = {
            'knowledge_index': self.knowledge_index,
            'knowledge_question_index': self.knowledge_question_index,
            'question_index': self.question_index,
            'chapter_index': self.chapter_index
        }
        with open(output_path, 'wb') as f:
            pickle.dump(indices, f)
        print(f"索引已保存到 {output_path}")
    
    @classmethod
    def load_indices(cls, input_path: str = 'indices.pkl') -> 'KnowledgeIndexSystem':
        """从文件加载索引
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            加载好索引的KnowledgeIndexSystem对象
        """
        with open(input_path, 'rb') as f:
            indices = pickle.load(f)
        
        system = cls()
        system.knowledge_index = indices['knowledge_index']
        system.knowledge_question_index = indices['knowledge_question_index']
        system.question_index = indices['question_index']
        system.chapter_index = indices['chapter_index']
        return system
    
    @classmethod
    async def load_indices_async(cls, input_path: str = 'indices.pkl') -> 'KnowledgeIndexSystem':
        """从文件异步加载索引
        
        Args:
            input_path: 输入文件路径
            
        Returns:
            加载好索引的KnowledgeIndexSystem对象
        """
        def _load():
            with open(input_path, 'rb') as f:
                return pickle.load(f)
        
        # 使用线程池执行IO操作
        indices = await asyncio.to_thread(_load)
        
        system = cls()
        system.knowledge_index = indices['knowledge_index']
        system.knowledge_question_index = indices['knowledge_question_index']
        system.question_index = indices['question_index']
        system.chapter_index = indices['chapter_index']
        return system


if __name__ == '__main__':
    # 假设我们在autodl-tmp/EasyDS/data/ds_data/data_processing目录下运行脚本
    system = KnowledgeIndexSystem(data_dir="/root/autodl-tmp/EasyDS/data/ds_data")
    system.build_indices()
    system.save_indices('/root/autodl-tmp/EasyDS/data/ds_data/ds_indices.pkl')
    
    # 示例：使用索引查询知识点和题目
    # 测试查询知识点
    test_kp_id = "kc0111"
    kp = system.get_knowledge_point(test_kp_id)
    if kp:
        print(f"\n知识点 {test_kp_id}: {kp['title']}")
        
        # 测试查询该知识点下的题目
        questions = system.get_questions_by_knowledge(test_kp_id)
        print(f"该知识点下有 {len(questions)} 个题目")
        for i, q in enumerate(questions[:3], 1):  # 只显示前3个
            print(f"{i}. 题目ID: {q['id']}, 标题: {q['title']}") 