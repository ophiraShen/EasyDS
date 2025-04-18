document.addEventListener('DOMContentLoaded', function() {
    // 加载章节信息
    loadChapterInfo();
    
    // 加载问题列表
    loadQuestions();
    
    // 返回按钮事件
    document.getElementById('back-btn').addEventListener('click', () => {
        window.location.href = '/';
    });
    
    // 加载章节信息
    async function loadChapterInfo() {
        try {
            const response = await fetch('/api/chapters');
            const chapters = await response.json();
            
            const chapter = chapters.find(c => c.id === chapterId);
            if (chapter) {
                document.getElementById('chapter-title').textContent = `${chapter.id}. ${chapter.title}`;
                document.title = `EasyDS - ${chapter.title}`;
            }
        } catch (error) {
            console.error('加载章节信息失败:', error);
        }
    }
    
    // 加载问题列表
    async function loadQuestions() {
        try {
            const response = await fetch(`/api/chapters/${chapterId}/questions`);
            const questions = await response.json();
            
            const questionsList = document.getElementById('questions-list');
            questionsList.innerHTML = '';
            
            if (questions.length === 0) {
                questionsList.innerHTML = '<div class="no-data">暂无题目</div>';
                return;
            }
            
            questions.forEach((question, index) => {
                const questionItem = document.createElement('div');
                questionItem.className = 'question-item';
                
                const difficulty = question.difficulty || '中等';
                const difficultyClass = difficulty === '简单' ? 'easy' : (difficulty === '困难' ? 'hard' : 'medium');
                
                questionItem.innerHTML = `
                    <div class="question-title">${index + 1}. ${question.title}</div>
                    <div class="question-meta">
                        <span class="question-type">${question.type || '选择题'}</span>
                        <span class="question-difficulty ${difficultyClass}">${difficulty}</span>
                    </div>
                `;
                
                questionItem.addEventListener('click', () => {
                    window.location.href = `/chat/${question.id}`;
                });
                
                questionsList.appendChild(questionItem);
            });
            
        } catch (error) {
            console.error('加载问题失败:', error);
            const questionsList = document.getElementById('questions-list');
            questionsList.innerHTML = '<div class="error">加载失败，请刷新重试</div>';
        }
    }
}); 