# src/web_demo.py
import os
import sys
import asyncio
from fastapi import FastAPI, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn
from typing import List, Dict, Optional
import json

sys.path.append("/root/autodl-tmp/EasyDS")
from src.knowledge_qa_system import KnowledgeQASystem

app = FastAPI(title="EasyDS Web演示")
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static") 

qa_system = KnowledgeQASystem()

# 创建必要的目录
os.makedirs("templates", exist_ok=True)
os.makedirs("static", exist_ok=True)

# 写入HTML模板
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>EasyDS 知识问答系统</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 0 auto; padding: 20px; }
        .container { display: flex; }
        .sidebar { width: 30%; padding-right: 20px; }
        .main { width: 70%; }
        .chapter { margin-bottom: 10px; cursor: pointer; padding: 8px; background: #f0f0f0; border-radius: 4px; }
        .chapter:hover { background: #e0e0e0; }
        .question { margin-bottom: 5px; cursor: pointer; padding: 5px; }
        .question:hover { background: #f0f0f0; }
        .chat-container { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: auto; margin-bottom: 10px; }
        .message { margin-bottom: 10px; }
        .user-message { text-align: right; }
        .user-bubble { background: #dcf8c6; padding: 8px; border-radius: 8px; display: inline-block; max-width: 80%; }
        .ai-message { text-align: left; }
        .ai-bubble { background: #f0f0f0; padding: 8px; border-radius: 8px; display: inline-block; max-width: 80%; }
        .input-container { display: flex; }
        input[type="text"] { flex-grow: 1; padding: 8px; }
        button { padding: 8px 16px; background: #4CAF50; color: white; border: none; cursor: pointer; }
        .question-detail { margin-bottom: 20px; }
        .hidden { display: none; }
        .options label { display: block; margin-bottom: 5px; }
    </style>
</head>
<body>
    <h1>EasyDS 知识问答系统</h1>
    
    <div class="container">
        <div class="sidebar">
            <h2>章节列表</h2>
            <div id="chapters-list"></div>
            
            <h2>问题列表</h2>
            <div id="questions-list"></div>
        </div>
        
        <div class="main">
            <div id="question-detail" class="question-detail hidden">
                <h2 id="question-title"></h2>
                <p id="question-content"></p>
                <div id="question-options" class="hidden">
                    <h3>选项:</h3>
                    <form id="options-form"></form>
                </div>
            </div>
            
            <div id="chat-section" class="hidden">
                <h2>对话</h2>
                <div id="chat-container" class="chat-container"></div>
                <div class="input-container">
                    <input type="text" id="user-input" placeholder="输入你的回答...">
                    <button id="send-btn">发送</button>
                </div>
            </div>
            
            <div id="knowledge-points" class="hidden">
                <h2>相关知识点</h2>
                <div id="knowledge-points-list"></div>
            </div>
            
            <div id="similar-questions" class="hidden">
                <h2>相似问题</h2>
                <div id="similar-questions-list"></div>
            </div>
        </div>
    </div>
    
    <script>
        // 全局变量
        let currentSessionId = null;
        let currentQuestionId = null;
        
        // 加载章节列表
        async function loadChapters() {
            const response = await fetch('/api/chapters');
            const chapters = await response.json();
            
            const chaptersListDiv = document.getElementById('chapters-list');
            chaptersListDiv.innerHTML = '';
            
            chapters.forEach(chapter => {
                const chapterDiv = document.createElement('div');
                chapterDiv.className = 'chapter';
                chapterDiv.innerText = chapter.title;
                chapterDiv.onclick = () => loadQuestions(chapter.id);
                chaptersListDiv.appendChild(chapterDiv);
            });
        }
        
        // 加载问题列表
        async function loadQuestions(chapterId) {
            const response = await fetch(`/api/chapters/${chapterId}/questions`);
            const questions = await response.json();
            
            const questionsListDiv = document.getElementById('questions-list');
            questionsListDiv.innerHTML = '';
            
            questions.forEach(question => {
                const questionDiv = document.createElement('div');
                questionDiv.className = 'question';
                questionDiv.innerText = question.title;
                questionDiv.onclick = () => loadQuestionDetail(question.id);
                questionsListDiv.appendChild(questionDiv);
            });
        }
        
        // 加载问题详情
        async function loadQuestionDetail(questionId) {
            currentQuestionId = questionId;
            
            const response = await fetch(`/api/questions/${questionId}`);
            const question = await response.json();
            
            // 显示问题详情
            document.getElementById('question-detail').classList.remove('hidden');
            document.getElementById('question-title').innerText = question.title;
            document.getElementById('question-content').innerText = question.content;
            
            // 如果有选项，显示选项
            const optionsDiv = document.getElementById('question-options');
            const optionsForm = document.getElementById('options-form');
            
            if (question.options && Object.keys(question.options).length > 0) {
                optionsDiv.classList.remove('hidden');
                optionsForm.innerHTML = '';
                
                Object.entries(question.options).forEach(([key, value]) => {
                    const label = document.createElement('label');
                    const input = document.createElement('input');
                    input.type = 'radio';
                    input.name = 'option';
                    input.value = key;
                    
                    label.appendChild(input);
                    label.appendChild(document.createTextNode(` ${key}. ${value}`));
                    optionsForm.appendChild(label);
                });
                
                // 添加提交按钮
                const submitButton = document.createElement('button');
                submitButton.type = 'button';
                submitButton.innerText = '提交答案';
                submitButton.onclick = submitAnswer;
                optionsForm.appendChild(submitButton);
            } else {
                optionsDiv.classList.add('hidden');
            }
            
            // 创建新会话
            const sessionResponse = await fetch('/api/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question_id: questionId })
            });
            
            const sessionData = await sessionResponse.json();
            currentSessionId = sessionData.session_id;
            
            // 清空聊天区域
            document.getElementById('chat-container').innerHTML = '';
            document.getElementById('chat-section').classList.remove('hidden');
            
            // 加载相关知识点
            loadKnowledgePoints(questionId);
            
            // 加载相似问题
            loadSimilarQuestions(questionId);
        }
        
        // 提交答案
        async function submitAnswer() {
            const selectedOption = document.querySelector('input[name="option"]:checked');
            if (!selectedOption) {
                alert('请选择一个选项');
                return;
            }
            
            const answer = selectedOption.value;
            await sendMessage(answer);
        }
        
        // 发送消息并接收回复
        async function sendMessage(message) {
            if (!currentSessionId) return;
            
            // 显示用户消息
            addUserMessage(message);
            
            // 发送到服务器
            const response = await fetch(`/api/sessions/${currentSessionId}/answer`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ answer: message })
            });
            
            // 处理流式响应
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let aiMessage = '';
            
            // 创建AI消息气泡
            const aiMessageDiv = document.createElement('div');
            aiMessageDiv.className = 'ai-message';
            const aiBubble = document.createElement('div');
            aiBubble.className = 'ai-bubble';
            aiMessageDiv.appendChild(aiBubble);
            document.getElementById('chat-container').appendChild(aiMessageDiv);
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const text = decoder.decode(value);
                const lines = text.split('\\n\\n');
                
                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') {
                            break;
                        }
                        
                        try {
                            const jsonData = JSON.parse(data);
                            if (jsonData.content) {
                                aiMessage += jsonData.content;
                                aiBubble.innerText = aiMessage;
                                
                                // 滚动到底部
                                const chatContainer = document.getElementById('chat-container');
                                chatContainer.scrollTop = chatContainer.scrollHeight;
                            }
                        } catch (e) {
                            console.error('Error parsing JSON:', e);
                        }
                    }
                }
            }
        }
        
        // 添加用户消息
        function addUserMessage(message) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'user-message message';
            
            const bubble = document.createElement('div');
            bubble.className = 'user-bubble';
            bubble.innerText = message;
            
            messageDiv.appendChild(bubble);
            chatContainer.appendChild(messageDiv);
            
            // 滚动到底部
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        // 加载相关知识点
        async function loadKnowledgePoints(questionId) {
            const response = await fetch(`/api/questions/${questionId}/knowledge-points`);
            const knowledgePoints = await response.json();
            
            const knowledgePointsDiv = document.getElementById('knowledge-points');
            const knowledgePointsList = document.getElementById('knowledge-points-list');
            
            if (knowledgePoints.length > 0) {
                knowledgePointsDiv.classList.remove('hidden');
                knowledgePointsList.innerHTML = '';
                
                knowledgePoints.forEach(kp => {
                    const kpDiv = document.createElement('div');
                    kpDiv.innerHTML = `<strong>${kp.title}</strong>: ${kp.summry}`;
                    knowledgePointsList.appendChild(kpDiv);
                });
            } else {
                knowledgePointsDiv.classList.add('hidden');
            }
        }
        
        // 加载相似问题
        async function loadSimilarQuestions(questionId) {
            const response = await fetch(`/api/questions/${questionId}/similar`);
            const similarQuestions = await response.json();
            
            const similarQuestionsDiv = document.getElementById('similar-questions');
            const similarQuestionsList = document.getElementById('similar-questions-list');
            
            if (similarQuestions.length > 0) {
                similarQuestionsDiv.classList.remove('hidden');
                similarQuestionsList.innerHTML = '';
                
                similarQuestions.forEach(q => {
                    const qDiv = document.createElement('div');
                    qDiv.className = 'question';
                    qDiv.innerText = q.title;
                    qDiv.onclick = () => loadQuestionDetail(q.id);
                    similarQuestionsList.appendChild(qDiv);
                });
            } else {
                similarQuestionsDiv.classList.add('hidden');
            }
        }
        
        // 发送按钮事件
        document.getElementById('send-btn').addEventListener('click', () => {
            const input = document.getElementById('user-input');
            const message = input.value.trim();
            
            if (message) {
                sendMessage(message);
                input.value = '';
            }
        });
        
        // Enter键发送
        document.getElementById('user-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const input = document.getElementById('user-input');
                const message = input.value.trim();
                
                if (message) {
                    sendMessage(message);
                    input.value = '';
                }
            }
        });
        
        // 页面加载时获取章节列表
        window.onload = loadChapters;
    </script>
</body>
</html>
    """)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# API路由 - 转发到QA系统
@app.get("/api/chapters")
async def api_chapters():
    return qa_system.get_chapters()

@app.get("/api/chapters/{chapter_id}/questions")
async def api_questions(chapter_id: str):
    return qa_system.get_questions_by_chapter(chapter_id)

@app.get("/api/questions/{question_id}")
async def api_question_detail(question_id: str):
    question = qa_system.get_question_detail(question_id)
    if not question:
        return {"error": f"找不到问题: {question_id}"}
    return question

@app.post("/api/sessions")
async def api_create_session(data: dict):
    try:
        session_id = qa_system.create_session(data["question_id"])
        return {"session_id": session_id}
    except ValueError as e:
        return {"error": str(e)}

@app.post("/api/sessions/{session_id}/answer")
async def api_answer_question(session_id: str, data: dict):
    try:
        async def stream_response():
            async for chunk in qa_system.process_answer(session_id, data["answer"]):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        
        return StreamingResponse(
            stream_response(),
            media_type="text/event-stream"
        )
    except ValueError as e:
        return {"error": str(e)}

@app.get("/api/questions/{question_id}/knowledge-points")
async def api_knowledge_points(question_id: str):
    return qa_system.get_related_knowledge_points(question_id)

@app.get("/api/questions/{question_id}/similar")
async def api_similar_questions(question_id: str):
    return qa_system.get_similar_questions(question_id)

if __name__ == "__main__":
    uvicorn.run("web_demo:app", host="0.0.0.0", port=8080, reload=True)