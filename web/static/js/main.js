document.addEventListener('DOMContentLoaded', function() {
    // 加载章节列表
    loadChapters();
    
    // 加载章节
    async function loadChapters() {
        try {
            const response = await fetch('/api/chapters');
            const chapters = await response.json();
            
            const chaptersList = document.getElementById('chapters-list');
            chaptersList.innerHTML = '';
            
            chapters.forEach(chapter => {
                const chapterItem = document.createElement('div');
                chapterItem.className = 'chapter-item';
                chapterItem.textContent = `${chapter.id}. ${chapter.title}`;
                chapterItem.addEventListener('click', () => {
                    window.location.href = `/chapter/${chapter.id}`;
                });
                
                chaptersList.appendChild(chapterItem);
            });
            
        } catch (error) {
            console.error('加载章节失败:', error);
            const chaptersList = document.getElementById('chapters-list');
            chaptersList.innerHTML = '<div class="error">加载失败，请刷新重试</div>';
        }
    }
}); 