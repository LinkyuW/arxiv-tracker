/**
 * arXiv 论文追踪器 - 前端主程序
 */

// API配置
const API_BASE_URL = 'http://localhost:5000/api';

// DOM元素缓存
const elements = {
    searchInput: document.getElementById('searchInput'),
    searchBtn: document.getElementById('searchBtn'),
    clearBtn: document.getElementById('clearBtn'),
    aiSummaryCheckbox: document.getElementById('aiSummary'),
    enableAuthorityCheckbox: document.getElementById('enableAuthority'),
    maxResultsSelect: document.getElementById('maxResults'),
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    stats: document.getElementById('stats'),
    resultCount: document.getElementById('resultCount'),
    results: document.getElementById('results'),
    cacheStatsLink: document.getElementById('cacheStats'),
    
    // 模态框
    statsModal: document.getElementById('statsModal'),
    detailModal: document.getElementById('detailModal'),
    statsContent: document.getElementById('statsContent'),
    statsClose: document.querySelector('#statsModal .close'),
    detailClose: document.querySelector('#detailModal .close'),
};

// 状态管理
let appState = {
    currentPapers: [],
    isLoading: false,
};

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', () => {
    attachEventListeners();
    loadCachedSearch();
});

function attachEventListeners() {
    elements.searchBtn.addEventListener('click', handleSearch);
    elements.clearBtn.addEventListener('click', handleClear);
    elements.searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    elements.cacheStatsLink.addEventListener('click', handleShowCacheStats);
    elements.statsClose.addEventListener('click', () => hideModal(elements.statsModal));
    elements.detailClose.addEventListener('click', () => hideModal(elements.detailModal));
    
    // 模态框外点击关闭
    window.addEventListener('click', (e) => {
        if (e.target === elements.statsModal) hideModal(elements.statsModal);
        if (e.target === elements.detailModal) hideModal(elements.detailModal);
    });
}

// ==================== 搜索功能 ====================

async function handleSearch() {
    const query = elements.searchInput.value.trim();
    
    if (!query) {
        showError('请输入搜索关键词');
        return;
    }
    
    showLoading(true);
    hideError();
    
    try {
        const maxResults = parseInt(elements.maxResultsSelect.value);
        const enableAuthority = elements.enableAuthorityCheckbox.checked;
        
        // 构建查询参数
        const params = new URLSearchParams({
            query: query,
            max_results: maxResults,
            enable_authority: enableAuthority ? 'true' : 'false',
            sort_by: enableAuthority ? 'authority' : 'date'
        });
        
        // 调用API搜索论文
        const response = await fetch(
            `${API_BASE_URL}/search?${params.toString()}`
        );
        
        if (!response.ok) {
            throw new Error('搜索失败，请重试');
        }
        
        const data = await response.json();
        
        if (data.status !== 'success' || !data.data) {
            throw new Error(data.message || '搜索失败');
        }
        
        const papers = data.data;
        appState.currentPapers = papers;
        
        // 保存搜索到本地存储
        localStorage.setItem('lastSearch', JSON.stringify({
            query,
            maxResults,
            aiSummary: elements.aiSummaryCheckbox.checked,
            enableAuthority: elements.enableAuthorityCheckbox.checked,
            timestamp: Date.now()
        }));
        
        // 如果启用AI总结，则获取总结
        if (elements.aiSummaryCheckbox.checked && papers.length > 0) {
            await fetchAISummaries(papers);
        }
        
        // 显示结果
        displayResults(papers);
        showStats(papers.length, data.from_cache, data.sort_by);
        
    } catch (error) {
        showError(`搜索出错: ${error.message}`);
        console.error('Search error:', error);
    } finally {
        showLoading(false);
    }
}

function handleClear() {
    elements.searchInput.value = '';
    elements.results.innerHTML = '';
    hideStats();
    hideError();
    localStorage.removeItem('lastSearch');
}

// ==================== API调用 ====================

async function fetchAISummaries(papers) {
    try {
        const paperData = papers.map(p => ({
            arxiv_id: p.arxiv_id,
            title: p.title,
            summary: p.summary
        }));
        
        const response = await fetch(`${API_BASE_URL}/summarize`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                papers: paperData,
                max_length: 200
            })
        });
        
        if (response.ok) {
            const data = await response.json();
            
            // 将AI总结合并到papers中
            if (data.data && Array.isArray(data.data)) {
                const summaryMap = {};
                data.data.forEach(item => {
                    summaryMap[item.arxiv_id] = item.summary;
                });
                
                appState.currentPapers = papers.map(p => ({
                    ...p,
                    ai_summary: summaryMap[p.arxiv_id] || null
                }));
            }
        }
    } catch (error) {
        console.error('AI summarization error:', error);
        // 继续显示论文，即使AI总结失败
    }
}

// ==================== 显示结果 ====================

function displayResults(papers) {
    if (!papers || papers.length === 0) {
        elements.results.innerHTML = '<p style="grid-column: 1/-1; text-align: center; padding: 2rem;">未找到相关论文</p>';
        return;
    }
    
    elements.results.innerHTML = papers.map(paper => createPaperCard(paper)).join('');
    
    // 添加点击事件
    document.querySelectorAll('.paper-card').forEach((card, index) => {
        card.addEventListener('click', () => showPaperDetail(papers[index]));
    });
}

function createPaperCard(paper) {
    const date = new Date(paper.published);
    const formattedDate = date.toLocaleDateString('zh-CN');
    
    // 构建权威性标签
    let authorityBadges = '';
    if (paper.badges && paper.badges.length > 0) {
        authorityBadges = paper.badges.map(badge => 
            `<span class="badge badge-${badge.toLowerCase()}">${badge}</span>`
        ).join('');
    }
    
    // 构建权威性等级显示
    let authorityDisplay = '';
    if (paper.authority_score !== undefined) {
        const score = paper.authority_score;
        const level = paper.level || '○';
        let scoreColor = 'gray';
        if (score >= 85) scoreColor = 'red';
        else if (score >= 70) scoreColor = 'orange';
        else if (score >= 50) scoreColor = 'yellow';
        
        authorityDisplay = `
            <div class="authority-badge">
                <span class="authority-score" style="color: ${scoreColor};">${level} ${score}分</span>
            </div>
        `;
    }
    
    return `
        <div class="paper-card">
            <div class="paper-card-header">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <div class="paper-id">${paper.arxiv_id}</div>
                        <div class="paper-title">${escapeHtml(paper.title)}</div>
                    </div>
                    ${authorityDisplay}
                </div>
                <div class="paper-meta">
                    <strong>发布:</strong> ${formattedDate}
                </div>
                ${paper.categories ? `<span class="paper-category">${paper.categories}</span>` : ''}
                ${authorityBadges ? `<div class="badges-container">${authorityBadges}</div>` : ''}
            </div>
            
            <div class="paper-summary">
                ${escapeHtml(paper.summary || '暂无摘要')}
            </div>
            
            <div class="paper-actions">
                <button onclick="window.open('${paper.url}', '_blank')">View</button>
                <button onclick="window.open('${paper.pdf_url}', '_blank')">PDF</button>
            </div>
        </div>
    `;
}

function showPaperDetail(paper) {
    const date = new Date(paper.published);
    const formattedDate = date.toLocaleDateString('zh-CN');
    
    document.getElementById('detailTitle').textContent = paper.title;
    document.getElementById('detailAuthors').textContent = 
        (paper.authors || []).join(', ') || '未知作者';
    document.getElementById('detailDate').textContent = formattedDate;
    document.getElementById('detailCategory').textContent = paper.categories || '未分类';
    document.getElementById('detailSummary').textContent = paper.summary || '暂无摘要';
    document.getElementById('detailPdfLink').href = paper.pdf_url;
    document.getElementById('detailArxivLink').href = paper.url;
    
    // 显示权威性信息
    const authoritySection = document.getElementById('authoritySection');
    if (paper.authority_score !== undefined) {
        document.getElementById('detailAuthorityScore').textContent = 
            `${paper.authority_score}/100`;
        document.getElementById('detailAuthorityLevel').textContent = 
            paper.level || '未评分';
        document.getElementById('detailCitations').textContent = 
            paper.citation_count || '未知';
        document.getElementById('detailAuthorityReasons').textContent = 
            (paper.reasons || []).join('; ') || '无';
        authoritySection.classList.remove('hidden');
    } else {
        authoritySection.classList.add('hidden');
    }
    
    // 显示AI总结
    const aiSummarySection = document.getElementById('aiSummarySection');
    if (paper.ai_summary) {
        document.getElementById('detailAISummary').textContent = paper.ai_summary;
        aiSummarySection.classList.remove('hidden');
    } else {
        aiSummarySection.classList.add('hidden');
    }
    
    showModal(elements.detailModal);
}

// ==================== 统计信息 ====================

async function handleShowCacheStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/cache/stats`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.data;
            elements.statsContent.innerHTML = `
                <div class="modal-meta">
                    <p><strong>缓存文件数:</strong> ${stats.file_count}</p>
                    <p><strong>缓存大小:</strong> ${stats.total_size_mb} MB</p>
                </div>
                <button class="btn btn-secondary" onclick="clearCache()">清空缓存</button>
            `;
            showModal(elements.statsModal);
        }
    } catch (error) {
        showError('获取缓存统计信息失败');
        console.error('Cache stats error:', error);
    }
}

async function clearCache() {
    try {
        const response = await fetch(`${API_BASE_URL}/cache/clear`, {
            method: 'POST'
        });
        
        if (response.ok) {
            alert('缓存已清空');
            hideModal(elements.statsModal);
        }
    } catch (error) {
        showError('清空缓存失败');
    }
}

function showStats(count, fromCache, sortBy) {
    elements.resultCount.textContent = count;
    elements.stats.classList.remove('hidden');
    
    let cacheText = fromCache ? ' (来自缓存)' : '';
    let sortText = sortBy === 'authority' ? '按权威性排序' : '按日期排序';
    
    elements.stats.textContent = `找到 ${count} 篇论文 - ${sortText}${cacheText}`;
}

function hideStats() {
    elements.stats.classList.add('hidden');
}

// ==================== 错误处理 ====================

function showError(message) {
    elements.error.textContent = message;
    elements.error.classList.remove('hidden');
}

function hideError() {
    elements.error.classList.add('hidden');
}

// ==================== 加载指示器 ====================

function showLoading(show) {
    appState.isLoading = show;
    if (show) {
        elements.loading.classList.remove('hidden');
    } else {
        elements.loading.classList.add('hidden');
    }
}

// ==================== 模态框 ====================

function showModal(modal) {
    modal.classList.remove('hidden');
}

function hideModal(modal) {
    modal.classList.add('hidden');
}

// ==================== 工具函数 ====================

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function loadCachedSearch() {
    const lastSearch = localStorage.getItem('lastSearch');
    
    if (lastSearch) {
        try {
            const search = JSON.parse(lastSearch);
            // 可以选择在加载时自动进行上次搜索
            // handleSearch();
        } catch (error) {
            console.error('Error loading cached search:', error);
        }
    }
}

// ==================== 导出函数供HTML调用 ====================

window.clearCache = clearCache;
window.showPaperDetail = showPaperDetail;
