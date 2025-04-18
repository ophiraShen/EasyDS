document.addEventListener('DOMContentLoaded', function() {
    // 存储章节数据
    let chapters = [];
    let currentChapter = null;
    
    // 获取DOM元素
    const chapterList = document.getElementById('chapter-list');
    const questionList = document.getElementById('question-list');
    const currentChapterTitle = document.getElementById('current-chapter-title');
    
    // 配置marked选项
    marked.use({
        breaks: true,  // 允许在换行时添加<br>标签
        gfm: true      // 使用GitHub风格的Markdown
    });
    
    // 初始化
    init();
    
    async function init() {
        try {
            // 加载章节数据
            await loadChapters();
        } catch (error) {
            console.error('初始化失败:', error);
            questionList.innerHTML = '<p class="empty-tip">加载失败，请刷新页面重试</p>';
        }
    }
    
    // 加载章节列表
    async function loadChapters() {
        try {
            const response = await fetch('/api/chapters');
            if (!response.ok) {
                throw new Error('获取章节数据失败');
            }
            
            chapters = await response.json();
            renderChapters();
        } catch (error) {
            console.error('加载章节失败:', error);
            chapterList.innerHTML = '<li class="empty-tip">加载章节失败，请刷新重试</li>';
        }
    }
    
    // 渲染章节列表
    function renderChapters() {
        chapterList.innerHTML = '';
        
        chapters.forEach(chapter => {
            const li = document.createElement('li');
            li.className = 'chapter-item';
            li.dataset.id = chapter.id;
            li.textContent = `${chapter.id}. ${chapter.title}`;
            
            li.addEventListener('click', () => selectChapter(chapter));
            
            chapterList.appendChild(li);
        });
        
        // 默认选中第一个章节
        if (chapters.length > 0) {
            selectChapter(chapters[0]);
        }
    }
    
    // 选择章节
    function selectChapter(chapter) {
        currentChapter = chapter;
        
        // 更新UI
        const chapterItems = document.querySelectorAll('.chapter-item');
        chapterItems.forEach(item => {
            if (item.dataset.id === chapter.id) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 更新标题
        currentChapterTitle.textContent = ` - ${chapter.title}`;
        
        // 加载问题
        loadQuestions(chapter.id);
    }
    
    // 加载问题列表
    async function loadQuestions(chapterId) {
        try {
            questionList.innerHTML = '<p class="empty-tip">加载中...</p>';
            
            const response = await fetch(`/api/chapters/${chapterId}/questions`);
            if (!response.ok) {
                throw new Error('获取题目数据失败');
            }
            
            const questions = await response.json();
            renderQuestions(questions);
        } catch (error) {
            console.error('加载题目失败:', error);
            questionList.innerHTML = '<p class="empty-tip">加载题目失败，请重试</p>';
        }
    }
    
    // 渲染问题列表
    function renderQuestions(questions) {
        if (!questions || questions.length === 0) {
            questionList.innerHTML = '<p class="empty-tip">该章节暂无题目</p>';
            return;
        }
        
        questionList.innerHTML = '';
        
        questions.forEach(question => {
            const div = document.createElement('div');
            div.className = 'question-item';
            
            // 添加难度标签类
            let difficultyClass = 'medium';
            if (question.difficulty === '简单') {
                difficultyClass = 'easy';
            } else if (question.difficulty === '困难') {
                difficultyClass = 'hard';
            }
            
            // 使用Markdown渲染标题
            const titleHTML = marked.parse(question.title);
            // 去除<p>标签以保持样式一致性
            const formattedTitle = titleHTML.replace(/<\/?p>/g, '');
            
            div.innerHTML = `
                <div class="title">${formattedTitle}</div>
                <div class="meta">
                    <span>${question.type}</span>
                    <span class="difficulty ${difficultyClass}">${question.difficulty}</span>
                </div>
            `;
            
            // 点击跳转到问题详情页
            div.addEventListener('click', () => {
                window.location.href = `/chat/${question.id}`;
            });
            
            questionList.appendChild(div);
        });
    }
}); 