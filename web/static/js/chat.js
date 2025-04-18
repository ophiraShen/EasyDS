document.addEventListener('DOMContentLoaded', function() {
    // 获取URL参数中的问题ID
    let sessionId = null;
    
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
            messageElement = container.querySelector('.message-student:last-child');
            
            // 如果不存在，则创建新的
            if (!messageElement) {
                messageElement = document.createElement('div');
                messageElement.className = 'message-left message-student';
                messageElement.innerHTML = `
                    <div class="message-header">
                        <div class="message-icon">👨‍🎓</div>
                        <span>学生智能体</span>
                    </div>
                    <div class="message-content"></div>
                `;
                container.appendChild(messageElement);
            }
        } else if (type === 'teacher') {
            // 获取最后一个教师消息元素
            messageElement = container.querySelector('.message-teacher:last-child');
            
            // 如果不存在，则创建新的
            if (!messageElement) {
                messageElement = document.createElement('div');
                messageElement.className = 'message-right message-teacher';
                messageElement.innerHTML = `
                    <div class="message-header">
                        <div class="message-icon">👨‍🏫</div>
                        <span>教师智能体</span>
                    </div>
                    <div class="message-content"></div>
                `;
                container.appendChild(messageElement);
            }
        }
        
        // 更新消息内容
        if (messageElement) {
            const contentDiv = messageElement.querySelector('.message-content');
            contentDiv.textContent = content;
            
            // 滚动到底部
            scrollToBottom();
        }
    }
    
    // 添加用户消息到聊天界面
    function addUserMessage(message) {
        const container = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-left message-user';
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-icon">👤</div>
                <span>你</span>
            </div>
            <div class="message-content">${message}</div>
        `;
        
        container.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 添加系统消息到聊天界面
    function addSystemMessage(message) {
        const container = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message-left system-message';
        messageDiv.style.gridColumn = "1 / span 2"; // 跨两列
        messageDiv.textContent = message;
        
        container.appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 显示问题详情
    function displayQuestionDetail(questionData) {
        const detailDiv = document.getElementById('question-detail');
        
        let html = `<div class="question-title">${questionData.title}</div>`;
        html += `<div class="question-content">${questionData.content}</div>`;
        
        if (questionData.options) {
            html += '<div class="options">';
            for (const key in questionData.options) {
                html += `<div class="option"><span>${key}.</span> ${questionData.options[key]}</div>`;
            }
            html += '</div>';
        }
        
        detailDiv.innerHTML = html;
    }
    
    // 显示知识点
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
                            popup.textContent = summary;
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
}); 