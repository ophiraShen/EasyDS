document.addEventListener('DOMContentLoaded', function() {
    // 获取URL参数中的问题ID
    let sessionId = null;
    
    // 配置marked选项
    marked.use({
        breaks: true,  // 允许在换行时添加<br>标签
        gfm: true      // 使用GitHub风格的Markdown
    });
    
    // 初始化页面
    initPage();
    
    // 发送按钮事件
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // 返回按钮事件
    document.getElementById('back-btn').addEventListener('click', () => {
        window.location.href = "/problems";
    });
    
    // 用户输入按Enter发送
    document.getElementById('user-input').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 初始化页面，加载问题详情和创建会话
    async function initPage() {
        try {
            // 加载问题详情
            const questionResp = await fetch(`/api/questions/${questionId}`);
            if (!questionResp.ok) {
                throw new Error('加载问题失败');
            }
            const questionData = await questionResp.json();
            displayQuestionDetail(questionData);
            
            // 加载知识点
            loadKnowledgePoints();
            
            // 加载相似问题
            loadSimilarQuestions();
            
            // 创建会话
            const sessionResp = await fetch('/api/sessions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question_id: questionId})
            });
            
            if (!sessionResp.ok) {
                throw new Error('创建会话失败');
            }
            
            const sessionData = await sessionResp.json();
            sessionId = sessionData.session_id;
            
            // 显示系统欢迎消息
            addSystemMessage("欢迎来到EasyDS智能辅导系统！请输入你对这个问题的解答，我会给你提供反馈。");
            
        } catch (error) {
            console.error('初始化失败:', error);
            addSystemMessage("加载失败，请刷新页面重试。");
        }
    }
    
    // 加载知识点
    async function loadKnowledgePoints() {
        try {
            const response = await fetch(`/api/questions/${questionId}/knowledge-points`);
            if (!response.ok) {
                throw new Error('加载知识点失败');
            }
            const data = await response.json();
            displayKnowledgePoints(data);
        } catch (error) {
            console.error('加载知识点失败:', error);
        }
    }
    
    // 加载相似问题
    async function loadSimilarQuestions() {
        try {
            const response = await fetch(`/api/questions/${questionId}/similar`);
            if (!response.ok) {
                throw new Error('加载相似问题失败');
            }
            const data = await response.json();
            displaySimilarQuestions(data);
        } catch (error) {
            console.error('加载相似问题失败:', error);
        }
    }
    
    // 发送用户消息
    async function sendMessage() {
        const userInput = document.getElementById('user-input');
        const message = userInput.value.trim();
        
        if (!message || !sessionId) return;
        
        // 显示用户消息
        addUserMessage(message);
        userInput.value = '';
        
        // 禁用发送按钮
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = true;
        sendBtn.textContent = '思考中...';
        
        try {
            // 通过SSE接收流式响应
            const url = `/api/sessions/${sessionId}/messages`;
            const eventSource = new EventSource(`${url}?content=${encodeURIComponent(message)}&_t=${Date.now()}`);
            
            console.log("创建SSE连接:", url);
            
            // 初始化智能体消息内容
            let studentContent = '';
            let teacherContent = '';
            let currentStudentMessage = null;
            let currentTeacherMessage = null;
            
            // 监听消息事件
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    const content = data.content;
                    const node = data.node;
                    
                    console.log("收到SSE消息:", node);
                    
                    // 根据node类型(智能体)处理不同的消息
                    if (node === 'student_agent') {
                        // 学生智能体消息 - 左列
                        studentContent += content;
                        updateOrCreateMessage('student', studentContent);
                    } else if (node === 'teacher_agent') {
                        // 教师智能体消息 - 右列
                        teacherContent += content;
                        updateOrCreateMessage('teacher', teacherContent);
                    } else if (node === 'system') {
                        // 系统消息
                        addSystemMessage(content);
                    }
                } catch (err) {
                    console.error("处理SSE消息错误:", err, event.data);
                }
            };
            
            // 监听结束事件
            eventSource.addEventListener('end', function() {
                console.log("SSE连接结束");
                eventSource.close();
                // 恢复发送按钮
                sendBtn.disabled = false;
                sendBtn.textContent = '发送';
            });
            
            // 处理错误
            eventSource.onerror = function(error) {
                console.error('SSE错误:', error);
                eventSource.close();
                // 恢复发送按钮
                sendBtn.disabled = false;
                sendBtn.textContent = '发送';
                addSystemMessage("接收消息出错，请重试。");
            };
            
        } catch (error) {
            console.error('发送消息失败:', error);
            // 恢复发送按钮
            sendBtn.disabled = false;
            sendBtn.textContent = '发送';
            addSystemMessage("发送消息失败，请重试。");
        }
    }
    
    // 更新或创建消息
    function updateOrCreateMessage(type, content) {
        const container = document.getElementById('chat-messages');
        
        // 创建或获取消息元素
        let messageElement = null;
        
        if (type === 'student') {
            // 获取最后一个学生消息元素
            messageElement = container.querySelector('.message-item:last-child .message-content .student-avatar');
            
            // 如果不存在，则创建新的
            if (!messageElement) {
                messageElement = document.createElement('div');
                messageElement.className = 'message-item';
                messageElement.innerHTML = `
                    <div class="message-container">
                        <div class="message-content">
                            <div class="avatar student-avatar">
                                <svg class="avatar-icon student-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                                    <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path>
                                </svg>
                            </div>
                            <div class="message-bubble-container">
                                <div class="message-header">
                                    <span class="sender-name student-name">学生智能体</span>
                                </div>
                                <div class="message-bubble student-bubble">
                                    <div class="message-text"></div>
                                    <button class="expand-button">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                                            <polyline points="6 9 12 15 18 9"></polyline>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="connector-line"></div>
                `;
                container.appendChild(messageElement);
                
                // 获取实际的消息内容元素
                messageElement = container.querySelector('.message-item:last-child');
            } else {
                // 如果找到了student-avatar，向上查找到message-item
                messageElement = messageElement.closest('.message-item');
            }
        } else if (type === 'teacher') {
            // 获取最后一个教师消息元素
            messageElement = container.querySelector('.message-item:last-child .message-content .teacher-avatar');
            
            // 如果不存在，则创建新的
            if (!messageElement) {
                messageElement = document.createElement('div');
                messageElement.className = 'message-item';
                messageElement.innerHTML = `
                    <div class="message-container">
                        <div class="message-content">
                            <div class="avatar teacher-avatar">
                                <svg class="avatar-icon teacher-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <path d="M22 10v6M2 10l10-5 10 5-10 5z"></path>
                                    <path d="M6 12v5c0 2 2 3 6 3s6-1 6-3v-5"></path>
                                </svg>
                            </div>
                            <div class="message-bubble-container">
                                <div class="message-header">
                                    <span class="teacher-badge">教师指导</span>
                                    <span class="sender-name teacher-name">教师智能体</span>
                                </div>
                                <div class="message-bubble teacher-bubble">
                                    <div class="message-text"></div>
                                    <button class="expand-button">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                                            <polyline points="6 9 12 15 18 9"></polyline>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="connector-line"></div>
                `;
                container.appendChild(messageElement);
                
                // 获取实际的消息内容元素
                messageElement = container.querySelector('.message-item:last-child');
            } else {
                // 如果找到了teacher-avatar，向上查找到message-item
                messageElement = messageElement.closest('.message-item');
            }
        }
        
        // 更新消息内容，使用Markdown渲染
        if (messageElement) {
            const contentDiv = messageElement.querySelector('.message-text');
            // 使用Markdown渲染消息内容
            contentDiv.innerHTML = marked.parse(content);
            
            // 检查消息是否需要显示展开/折叠按钮
            const expandButton = messageElement.querySelector('.expand-button');
            if (expandButton) {
                // 延迟一小段时间确保内容已渲染，然后检查高度
                setTimeout(() => {
                    const contentHeight = contentDiv.scrollHeight;
                    const lineHeight = parseInt(window.getComputedStyle(contentDiv).lineHeight);
                    const maxHeight = lineHeight * 3; // 3行高度
                    
                    if (contentHeight > maxHeight) {
                        expandButton.style.display = 'inline-block';
                        contentDiv.classList.remove('expanded');
                    } else {
                        expandButton.style.display = 'none';
                    }
                    
                    // 滚动到底部
                    scrollToBottom();
                }, 100);
            }
            
            // 处理内容中的列表，确保它们显示在气泡内
            const lists = contentDiv.querySelectorAll('ol, ul');
            lists.forEach(list => {
                list.style.paddingLeft = '1.5rem';
                list.style.marginTop = '0.3rem';
                list.style.marginBottom = '0.3rem';
            });
            
            // 滚动到底部
            scrollToBottom();
        }
    }
    
    // 添加用户消息到聊天界面
    function addUserMessage(message) {
        const container = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-item';
        
        // 检查是否是短消息（少于15个字符）- 增加字符数限制
        const isShortMessage = message.length < 15;
        const shortTextClass = isShortMessage ? 'short-text' : '';
        
        // 创建临时元素，确保生成的内容不会被浏览器错误解析
        const tempDiv = document.createElement('div');
        tempDiv.textContent = message;
        const safeMessage = tempDiv.textContent;
        
        // 使用更安全的方式添加内容
        messageDiv.innerHTML = `
            <div class="message-container user">
                <div class="message-content">
                    <div class="avatar user-avatar">
                        <svg class="avatar-icon user-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                    <div class="message-bubble-container">
                        <div class="message-header">
                            <span class="sender-name user-name">你</span>
                        </div>
                        <div class="message-bubble user-bubble${isShortMessage ? ' short-message' : ''}">
                            <div class="message-text ${shortTextClass}"></div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="connector-line"></div>
        `;
        
        // 安全地设置消息内容
        const messageTextDiv = messageDiv.querySelector('.message-text');
        messageTextDiv.innerHTML = marked.parse(safeMessage);
        
        container.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 添加系统消息到聊天界面
    function addSystemMessage(message) {
        const container = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-item';
        
        messageDiv.innerHTML = `
            <div class="message-container">
                <div class="message-content">
                    <div class="avatar">
                        <svg class="avatar-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="12" y1="8" x2="12" y2="12"></line>
                            <line x1="12" y1="16" x2="12.01" y2="16"></line>
                        </svg>
                    </div>
                    <div class="message-bubble-container">
                        <div class="message-header">
                            <span class="sender-name">系统</span>
                        </div>
                        <div class="message-bubble">
                            <div class="message-text">${marked.parse(message)}</div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="connector-line"></div>
        `;
        
        container.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 显示问题详情 - 使用Markdown渲染
    function displayQuestionDetail(questionData) {
        const detailDiv = document.getElementById('question-detail');
        
        // 使用Markdown渲染标题和内容
        let html = `<div class="question-title">${questionData.title}</div>`;
        html += `<div class="question-content">${marked.parse(questionData.content)}</div>`;
        
        if (questionData.options) {
            html += '<div class="options">';
            for (const key in questionData.options) {
                // 选项也用Markdown渲染
                html += `<div class="option"><span>${key}.</span> ${marked.parse(questionData.options[key])}</div>`;
            }
            html += '</div>';
        }
        
        detailDiv.innerHTML = html;
    }
    
    // 显示知识点 - 使用Markdown渲染知识点内容
    function displayKnowledgePoints(kpData) {
        const kpList = document.getElementById('knowledge-points-list');
        kpList.innerHTML = '';
        
        if (!kpData || kpData.length === 0) {
            kpList.innerHTML = '<li>暂无相关知识点</li>';
            return;
        }
        
        kpData.forEach(kp => {
            const li = document.createElement('li');
            li.className = 'knowledge-point-item';
            li.dataset.id = kp.id;
            
            // 创建知识点标题元素
            const titleSpan = document.createElement('span');
            titleSpan.className = 'knowledge-point-title';
            titleSpan.textContent = kp.title;
            
            // 创建便签图标
            const noteIcon = document.createElement('span');
            noteIcon.className = 'note-icon';
            noteIcon.innerHTML = '<svg width="16" height="16" fill="currentColor" viewBox="0 0 16 16"><path d="M1 2.828c.885-.37 2.154-.769 3.388-.893 1.33-.134 2.458.063 3.112.752v9.746c-.935-.53-2.12-.603-3.213-.493-1.18.12-2.37.461-3.287.811V2.828zm7.5-.141c.654-.689 1.782-.886 3.112-.752 1.234.124 2.503.523 3.388.893v9.923c-.918-.35-2.107-.692-3.287-.81-1.094-.111-2.278-.039-3.213.492V2.687zM8 1.783C7.015.936 5.587.81 4.287.94c-1.514.153-3.042.672-3.994 1.105A.5.5 0 0 0 0 2.5v11a.5.5 0 0 0 .707.455c.882-.4 2.303-.881 3.68-1.02 1.409-.142 2.59.087 3.223.877a.5.5 0 0 0 .78 0c.633-.79 1.814-1.019 3.222-.877 1.378.139 2.8.62 3.681 1.02A.5.5 0 0 0 16 13.5v-11a.5.5 0 0 0-.293-.455c-.952-.433-2.48-.952-3.994-1.105C10.413.809 8.985.936 8 1.783z"/></svg>';
            
            li.appendChild(titleSpan);
            li.appendChild(noteIcon);
            
            // 创建浮窗便签元素
            const popup = document.createElement('div');
            popup.className = 'knowledge-popup';
            popup.textContent = '加载中...';
            popup.style.display = 'none';
            li.appendChild(popup);
            
            // 添加点击事件，切换浮窗显示状态
            li.addEventListener('click', async function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                // 如果已经显示，则隐藏
                if (popup.style.display === 'block') {
                    popup.style.display = 'none';
                    return;
                }
                
                // 显示浮窗
                popup.style.display = 'block';
                
                // 检查并调整浮窗位置，避免超出屏幕
                adjustPopupPosition(li, popup);
                
                // 如果还是"加载中..."，则加载详细内容
                if (popup.textContent === '加载中...') {
                    try {
                        const response = await fetch(`/api/knowledge/${kp.id}`);
                        if (response.ok) {
                            const summary = await response.json();
                            // 使用Markdown渲染知识点内容
                            popup.innerHTML = marked.parse(summary);
                        } else {
                            popup.textContent = '无法加载知识点详情';
                        }
                    } catch (error) {
                        console.error('加载知识点详情失败:', error);
                        popup.textContent = '加载知识点详情失败';
                    }
                }
            });
            
            // 点击文档其他地方关闭浮窗
            document.addEventListener('click', function(e) {
                if (!li.contains(e.target)) {
                    popup.style.display = 'none';
                }
            });
            
            kpList.appendChild(li);
        });
    }
    
    // 显示相似问题
    function displaySimilarQuestions(questions) {
        const qList = document.getElementById('similar-questions-list');
        qList.innerHTML = '';
        
        if (!questions || questions.length === 0) {
            qList.innerHTML = '<li>暂无相似问题</li>';
            return;
        }
        
        questions.forEach(q => {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = `/chat/${q.id}`;
            a.textContent = q.title;
            li.appendChild(a);
            qList.appendChild(li);
        });
    }
    
    // 调整浮窗位置
    function adjustPopupPosition(element, popup) {
        // 计算元素位置
        const rect = element.getBoundingClientRect();
        const popupWidth = popup.offsetWidth;
        
        // 检查右侧空间是否足够
        if (rect.left + popupWidth > window.innerWidth - 20) {
            // 如果右侧空间不足，将浮窗放在左侧
            popup.style.left = 'auto';
            popup.style.right = '0';
            
            // 调整指示箭头位置
            const arrow = popup.querySelector('.popup-arrow') || document.createElement('div');
            if (!arrow.classList.contains('popup-arrow')) {
                arrow.className = 'popup-arrow';
                popup.appendChild(arrow);
            }
            arrow.style.left = 'auto';
            arrow.style.right = '20px';
        } else {
            // 默认位置
            popup.style.left = '0';
            popup.style.right = 'auto';
        }
    }
    
    // 滚动到底部
    function scrollToBottom() {
        const notebookContent = document.querySelector('.notebook-content');
        if (notebookContent) {
            notebookContent.scrollTop = notebookContent.scrollHeight;
        }
    }
    
    // 为所有展开/折叠按钮添加点击事件
    document.addEventListener('click', function(e) {
        if (e.target.closest('.expand-button')) {
            const button = e.target.closest('.expand-button');
            const messageText = button.parentElement.querySelector('.message-text');
            
            messageText.classList.toggle('expanded');
            
            // 更新按钮图标
            if (messageText.classList.contains('expanded')) {
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                        <polyline points="18 15 12 9 6 15"></polyline>
                    </svg>
                `;
            } else {
                button.innerHTML = `
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="16" height="16">
                        <polyline points="6 9 12 15 18 9"></polyline>
                    </svg>
                `;
            }
            
            // 滚动到适当位置
            setTimeout(scrollToBottom, 100);
        }
    });
}); 