from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from web.api.endpoints import chapters, questions, sessions, knowledge

app = FastAPI(title="EasyDS API", description="数据结构智能教学API", version="1.0.0")

# 配置静态文件
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# 配置模板
templates = Jinja2Templates(directory="web/templates")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chapters.router, prefix="/api", tags=["chapters"])
app.include_router(questions.router, prefix="/api", tags=["questions"])
app.include_router(sessions.router, prefix="/api", tags=["sessions"])
app.include_router(knowledge.router, prefix="/api", tags=["knowledge"])

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/problems")
async def problems_page(request: Request):
    return templates.TemplateResponse("problems.html", {"request": request})

@app.get("/knowledge")
async def knowledge_page(request: Request):
    return templates.TemplateResponse("knowledge.html", {"request": request})

@app.get("/chat/{question_id}")
async def chat_view(request: Request, question_id: str):
    return templates.TemplateResponse("chat.html", {"request": request, "question_id": question_id})