document.addEventListener('DOMContentLoaded', function() {
    // 存储章节数据和知识点数据
    let chapters = [];
    let currentChapter = null;
    let knowledgePoints = {};
    
    // 获取DOM元素
    const chapterList = document.getElementById('chapter-list');
    const knowledgeList = document.getElementById('knowledge-list');
    const knowledgeDetail = document.getElementById('knowledge-detail');
    const knowledgeTitle = document.getElementById('knowledge-title');
    const knowledgeSummary = document.getElementById('knowledge-summary');
    const currentChapterTitle = document.getElementById('current-chapter-title');
    const backToListBtn = document.getElementById('back-to-list');
    
    // 初始化
    init();
    
    // 返回列表按钮事件
    backToListBtn.addEventListener('click', () => {
        knowledgeDetail.style.display = 'none';
        document.getElementById('knowledge-list-container').style.display = 'block';
    });
    
    async function init() {
        try {
            // 加载章节数据
            await loadChapters();
        } catch (error) {
            console.error('初始化失败:', error);
            knowledgeList.innerHTML = '<p class="empty-tip">加载失败，请刷新页面重试</p>';
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
            
            // 加载所有章节的知识点
            await loadAllKnowledgePoints();
        } catch (error) {
            console.error('加载章节失败:', error);
            chapterList.innerHTML = '<li class="empty-tip">加载章节失败，请刷新重试</li>';
        }
    }
    
    // 加载所有章节的知识点
    async function loadAllKnowledgePoints() {
        try {
            const response = await fetch('/api/knowledge/chapters');
            if (!response.ok) {
                throw new Error('获取知识点数据失败');
            }
            
            knowledgePoints = await response.json();
        } catch (error) {
            console.error('加载知识点失败:', error);
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
        
        // 回到知识点列表视图
        knowledgeDetail.style.display = 'none';
        document.getElementById('knowledge-list-container').style.display = 'block';
        
        // 加载该章节的知识点
        renderKnowledgePoints(chapter.id);
    }
    
    // 渲染知识点列表
    function renderKnowledgePoints(chapterId) {
        const chapterKnowledgePoints = knowledgePoints[chapterId] || [];
        
        if (!chapterKnowledgePoints || chapterKnowledgePoints.length === 0) {
            knowledgeList.innerHTML = '<p class="empty-tip">该章节暂无知识点</p>';
            return;
        }
        
        knowledgeList.innerHTML = '';
        
        chapterKnowledgePoints.forEach(kpId => {
            const div = document.createElement('div');
            div.className = 'knowledge-item';
            div.dataset.id = kpId;
            div.textContent = kpId;
            
            // 点击显示知识点详情
            div.addEventListener('click', () => {
                showKnowledgeDetail(kpId);
            });
            
            knowledgeList.appendChild(div);
        });
    }
    
    // 显示知识点详情
    async function showKnowledgeDetail(knowledgeId) {
        try {
            // 显示加载中
            knowledgeTitle.textContent = knowledgeId;
            knowledgeSummary.innerHTML = '<div style="text-align: center; padding: 20px;">加载中...</div>';
            knowledgeDetail.style.display = 'flex';
            document.getElementById('knowledge-list-container').style.display = 'none';
            
            // 获取知识点详情
            const response = await fetch(`/api/knowledge/${knowledgeId}`);
            if (!response.ok) {
                throw new Error('获取知识点详情失败');
            }
            
            const summary = await response.json();
            
            // 格式化内容（处理可能的Markdown风格文本）
            const formattedContent = formatKnowledgeContent(summary);
            
            // 更新UI
            knowledgeTitle.textContent = knowledgeId;
            knowledgeSummary.innerHTML = formattedContent;
        } catch (error) {
            console.error('加载知识点详情失败:', error);
            knowledgeSummary.innerHTML = '<div class="error-message">加载知识点详情失败，请重试</div>';
        }
    }
    
    // 格式化知识点内容，处理特殊标记
    function formatKnowledgeContent(content) {
        if (!content) return '';
        
        // 替换特殊标记为HTML
        let formatted = content
            // 处理段落分隔
            .replace(/\n\n/g, '</p><p>')
            // 处理定义项
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            // 处理序号列表
            .replace(/(\d+\.\s+)/g, '<br><span class="list-number">$1</span>');
        
        // 最后包装在段落标签中
        return `<p>${formatted}</p>`;
    }
}); 