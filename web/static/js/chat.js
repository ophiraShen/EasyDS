document.addEventListener('DOMContentLoaded', function() {
    // 获取URL参数中的问题ID
    let sessionId = null;
    
    // 初始化页面
    initPage();
    
    // 发送按钮事件
    document.getElementById('send-btn').addEventListener('click', sendMessage);
    
    // 返回按钮事件
    document.getElementById('back-btn').addEventListener('click', () => {
        window.history.back();
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
            // 准备当前响应容器
            const studentContainer = document.createElement('div');
            studentContainer.className = 'message student-message';
            studentContainer.style.display = 'none';
            
            const teacherContainer = document.createElement('div');
            teacherContainer.className = 'message teacher-message';
            teacherContainer.style.display = 'none';
            
            const chatMessages = document.getElementById('chat-messages');
            chatMessages.appendChild(studentContainer);
            chatMessages.appendChild(teacherContainer);
            
            // 通过SSE接收流式响应 - 使用POST方式替代原来的GET方式
            // 先构造URL，不附加参数
            const url = `/api/sessions/${sessionId}/messages`;
            
            // 在URL中添加当前时间戳，防止缓存问题
            const eventSource = new EventSource(`${url}?content=${encodeURIComponent(message)}&_t=${Date.now()}`);
            
            console.log("创建SSE连接:", url);
            
            let currentNode = null;
            
            // 监听消息事件
            eventSource.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    const content = data.content;
                    const node = data.node;
                    
                    console.log("收到SSE消息:", node);
                    
                    // 根据node类型(智能体)选择不同的显示容器
                    let container;
                    if (node === 'student_agent') {
                        container = studentContainer;
                        if (currentNode !== 'student_agent') {
                            // 首次显示学生智能体消息，添加标签
                            container.innerHTML = '<div class="agent-label">学生智能体:</div><div class="agent-content"></div>';
                            container.style.display = 'block';
                        }
                        currentNode = 'student_agent';
                    } else if (node === 'teacher_agent') {
                        container = teacherContainer;
                        if (currentNode !== 'teacher_agent') {
                            // 首次显示教师智能体消息，添加标签
                            container.innerHTML = '<div class="agent-label">教师智能体:</div><div class="agent-content"></div>';
                            container.style.display = 'block';
                        }
                        currentNode = 'teacher_agent';
                    } else if (node === 'system') {
                        // 添加系统消息处理
                        addSystemMessage(content);
                        return;
                    }
                    
                    // 更新消息内容
                    if (container) {
                        const contentDiv = container.querySelector('.agent-content');
                        contentDiv.textContent += content;
                    }
                    
                    // 自动滚动到底部
                    chatMessages.scrollTop = chatMessages.scrollHeight;
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
    
    // 添加用户消息到聊天界面
    function addUserMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message user-message';
        messageDiv.textContent = message;
        
        document.getElementById('chat-messages').appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 添加系统消息到聊天界面
    function addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system-message';
        messageDiv.textContent = message;
        
        document.getElementById('chat-messages').appendChild(messageDiv);
        scrollToBottom();
    }
    
    // 显示问题详情
    function displayQuestionDetail(questionData) {
        const detailDiv = document.getElementById('question-detail');
        
        let html = `<h3>${questionData.title}</h3>`;
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
            li.textContent = kp.title;
            li.title = kp.summry; // 使用title属性显示知识点概述
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
    
    // 滚动到底部
    function scrollToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}); 