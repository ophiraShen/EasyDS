document.addEventListener('DOMContentLoaded', function() {
    // 存储章节数据和知识点数据
    let chapters = [];
    let currentChapter = null;
    let knowledgePoints = {};
    let currentKnowledgeId = null;
    
    // 存储知识点详情信息（id和title）
    let knowledgeDetails = {};
    
    // 获取DOM元素
    const chapterList = document.getElementById('chapter-list');
    const knowledgeList = document.getElementById('knowledge-list');
    const knowledgeDetail = document.getElementById('knowledge-detail');
    const knowledgeTitle = document.getElementById('knowledge-title');
    const knowledgeSummary = document.getElementById('knowledge-summary');
    const currentChapterTitle = document.getElementById('current-chapter-title');
    const emptyDetailPlaceholder = document.getElementById('empty-detail-placeholder');
    
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
            
            // 加载所有知识点的标题
            await loadAllKnowledgeDetails();
        } catch (error) {
            console.error('初始化失败:', error);
            knowledgeList.innerHTML = '<p class="empty-tip">加载失败，请刷新页面重试</p>';
        }
    }
    
    // 加载所有知识点详情信息（标题）
    async function loadAllKnowledgeDetails() {
        try {
            const response = await fetch('/api/knowledge/details/all');
            if (!response.ok) {
                throw new Error('获取知识点详情数据失败');
            }
            
            knowledgeDetails = await response.json();
            console.log('已加载知识点详情信息:', Object.keys(knowledgeDetails).length);
        } catch (error) {
            console.error('加载知识点详情失败:', error);
            // 如果API调用失败，使用模拟数据作为备选
            simulateKnowledgeDetails();
        }
    }
    
    // 临时方法：模拟知识点标题数据
    // 仅在API调用失败时使用此备选方法
    function simulateKnowledgeDetails() {
        console.warn('使用模拟数据作为备选方案');
        // 初始化知识点详情映射
        let allKnowledgeIds = [];
        
        // 收集所有知识点ID
        for (const chapterId in knowledgePoints) {
            allKnowledgeIds = allKnowledgeIds.concat(knowledgePoints[chapterId]);
        }
        
        // 为每个知识点创建标题数据
        allKnowledgeIds.forEach(kpId => {
            // 一些知识点标题示例
            let title = "";
            
            if (kpId.startsWith("kc")) {
                title = "数据结构基本概念";
            } else if (kpId.startsWith("kl")) {
                title = "线性表";
            } else if (kpId.startsWith("ks")) {
                title = "栈和队列";
            } else if (kpId.startsWith("kt")) {
                title = "树和二叉树";
            } else if (kpId.startsWith("kg")) {
                title = "图";
            } else if (kpId.startsWith("ka")) {
                title = "算法分析";
            } else {
                title = "知识点";
            }
            
            // 将知识点ID和标题存储到映射中
            knowledgeDetails[kpId] = {
                id: kpId,
                title: title + " " + kpId.substring(2)
            };
        });
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
    
    // 获取知识点标题
    async function getKnowledgeTitle(knowledgeId) {
        // 如果已经有缓存的标题，直接返回
        if (knowledgeDetails[knowledgeId] && knowledgeDetails[knowledgeId].title) {
            return knowledgeDetails[knowledgeId].title;
        }
        
        // 否则从API获取
        try {
            const response = await fetch(`/api/knowledge/${knowledgeId}/title`);
            if (!response.ok) {
                throw new Error('获取知识点标题失败');
            }
            
            const data = await response.json();
            
            // 缓存结果
            if (!knowledgeDetails[knowledgeId]) {
                knowledgeDetails[knowledgeId] = {
                    id: knowledgeId,
                    title: data.title
                };
            } else {
                knowledgeDetails[knowledgeId].title = data.title;
            }
            
            return data.title;
        } catch (error) {
            console.error(`获取知识点 ${knowledgeId} 标题失败:`, error);
            return ""; // 失败时返回空标题
        }
    }
    
    // 渲染章节列表
    function renderChapters() {
        chapterList.innerHTML = '';
        
        chapters.forEach(chapter => {
            const li = document.createElement('li');
            li.className = 'chapter-item';
            li.dataset.id = chapter.id;
            
            // 添加章节标题和折叠图标
            const titleSpan = document.createElement('span');
            titleSpan.className = 'chapter-title';
            titleSpan.textContent = `${chapter.id}. ${chapter.title}`;
            
            const icon = document.createElement('i');
            icon.className = 'fas fa-chevron-right chapter-icon';
            
            li.appendChild(titleSpan);
            li.appendChild(icon);
            
            // 点击章节切换展开/折叠状态
            li.addEventListener('click', (e) => {
                e.preventDefault();
                toggleChapter(chapter, li);
            });
            
            chapterList.appendChild(li);
        });
    }
    
    // 切换章节展开/折叠状态
    function toggleChapter(chapter, chapterElement) {
        const wasActive = chapterElement.classList.contains('active');
        
        // 重置所有章节的状态
        const allChapters = document.querySelectorAll('.chapter-item');
        allChapters.forEach(item => {
            item.classList.remove('active', 'expanded');
        });
        
        // 如果当前章节之前不是活动的，或者是活动的但不是展开的，则展开它
        if (!wasActive) {
            chapterElement.classList.add('active', 'expanded');
            currentChapter = chapter;
            currentChapterTitle.textContent = ` - ${chapter.title}`;
            loadKnowledgePoints(chapter.id);
        } else {
            // 如果之前是活动的，则折叠它（清空知识点列表）
            currentChapter = null;
            currentChapterTitle.textContent = '';
            knowledgeList.innerHTML = '<p class="empty-tip">请选择章节查看知识点</p>';
        }
    }
    
    // 加载某章节的知识点
    function loadKnowledgePoints(chapterId) {
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
            
            // 获取知识点标题（如果存在）
            let kpTitle = knowledgeDetails[kpId] ? knowledgeDetails[kpId].title : "";
            
            // 创建知识点ID和标题元素
            const idSpan = document.createElement('span');
            idSpan.className = 'knowledge-id';
            idSpan.textContent = kpId;
            
            const titleDiv = document.createElement('div');
            titleDiv.className = 'knowledge-title-text';
            titleDiv.textContent = kpTitle;
            
            // 组合ID和标题
            div.appendChild(idSpan);
            div.appendChild(titleDiv);
            
            // 点击知识点显示详情
            div.addEventListener('click', (e) => {
                e.stopPropagation(); // 防止事件冒泡到章节
                selectKnowledgePoint(kpId, div);
            });
            
            knowledgeList.appendChild(div);
        });
    }
    
    // 选择知识点并显示详情
    function selectKnowledgePoint(knowledgeId, element) {
        // 更新UI选中状态
        const allKnowledgeItems = document.querySelectorAll('.knowledge-item');
        allKnowledgeItems.forEach(item => item.classList.remove('active'));
        if (element) element.classList.add('active');
        
        // 更新当前选中的知识点ID
        currentKnowledgeId = knowledgeId;
        
        // 显示知识点详情
        loadKnowledgeDetail(knowledgeId);
    }
    
    // 加载知识点详情
    async function loadKnowledgeDetail(knowledgeId) {
        try {
            // 隐藏占位符，显示详情面板
            emptyDetailPlaceholder.style.display = 'none';
            knowledgeDetail.style.display = 'flex';
            
            // 获取知识点标题
            const kpDetail = knowledgeDetails[knowledgeId] || { id: knowledgeId, title: "" };
            
            // 如果标题为空，尝试从API获取
            if (!kpDetail.title) {
                kpDetail.title = await getKnowledgeTitle(knowledgeId);
            }
            
            // 显示加载中
            knowledgeTitle.innerHTML = `<span class="knowledge-id-label">${kpDetail.id}</span>`;
            if (kpDetail.title) {
                knowledgeTitle.innerHTML += ` - <span class="knowledge-title-label">${kpDetail.title}</span>`;
            }
            
            knowledgeSummary.innerHTML = '<div style="text-align: center; padding: 20px;">加载中...</div>';
            
            // 获取知识点详情
            const response = await fetch(`/api/knowledge/${knowledgeId}`);
            if (!response.ok) {
                throw new Error('获取知识点详情失败');
            }
            
            const summary = await response.json();
            
            // 使用marked将Markdown转换为HTML
            const renderedHTML = marked.parse(summary);
            
            // 更新UI (仅更新内容，标题已在上面更新)
            knowledgeSummary.innerHTML = renderedHTML;
        } catch (error) {
            console.error('加载知识点详情失败:', error);
            knowledgeSummary.innerHTML = '<div class="error-message">加载知识点详情失败，请重试</div>';
        }
    }
}); 