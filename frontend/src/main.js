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
    apiResponse: null,  // 保存完整的API响应
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
        
        // 调用API搜索论文
        const response = await fetch(
            `${API_BASE_URL}/search?query=${encodeURIComponent(query)}&max_results=${maxResults}`
        );
        
        if (!response.ok) {
            throw new Error('搜索失败，请重试');
        }
        
        const data = await response.json();
        
        if (data.status !== 'success' || !data.data) {
            throw new Error(data.message || '搜索失败');
        }
        
        // 处理新的数据结构（可能包含trajectory_summary和quarterly_data）
        let papers = data.data;
        if (data.data.papers) {
            // 新的API格式：包含papers、trajectory_summary和quarterly_data
            papers = data.data.papers;
            appState.apiResponse = data.data;  // 保存完整响应
        }
        appState.currentPapers = papers;
        
        // 保存搜索到本地存储
        localStorage.setItem('lastSearch', JSON.stringify({
            query,
            maxResults,
            aiSummary: elements.aiSummaryCheckbox.checked,
            timestamp: Date.now()
        }));
        
        // 如果启用AI总结，则获取总结
        if (elements.aiSummaryCheckbox.checked && papers.length > 0) {
            await fetchAISummaries(papers);
        }
        
        // 显示结果
        displayResults(papers);
        showStats(papers.length, data.from_cache);
        
        // 如果有完整的API响应数据，显示发展脉络和季度汇总
        if (appState.apiResponse && appState.apiResponse.trajectory_summary !== undefined) {
            displayTrajectoryAndQuarterly(appState.apiResponse);
        }
        
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
    
    // 构建发表信息显示
    let publicationInfo = '';
    if (paper.publication_venue) {
        const venue = paper.publication_venue;
        const ccfGrade = paper.ccf_grade ? ` [CCF ${paper.ccf_grade}]` : '';
        publicationInfo = `<div class="publication-badge">${venue}${ccfGrade}</div>`;
    }
    
    // 构建引用次数显示
    let citationInfo = '';
    if (paper.citation_count !== null && paper.citation_count !== undefined) {
        citationInfo = `<span class="citation-count">${paper.citation_count} 引用</span>`;
    }
    
    return `
        <div class="paper-card">
            <div class="paper-card-header">
                <div class="paper-id">${paper.arxiv_id}</div>
                <div class="paper-title">${escapeHtml(paper.title)}</div>
                <div class="paper-meta">
                    <strong>发布:</strong> ${formattedDate}
                    ${citationInfo}
                </div>
                ${publicationInfo}
                ${paper.categories ? `<span class="paper-category">${paper.categories}</span>` : ''}
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
    
    // 显示发表信息
    const publicationSection = document.getElementById('publicationSection');
    if (paper.publication_venue) {
        document.getElementById('detailPublicationVenue').textContent = paper.publication_venue;
        document.getElementById('detailCCFGrade').textContent = paper.ccf_grade || '未知';
        document.getElementById('detailCitationCount').textContent = 
            paper.citation_count !== null && paper.citation_count !== undefined 
                ? `${paper.citation_count} 次` 
                : '未获取';
        publicationSection.classList.remove('hidden');
    } else {
        publicationSection.classList.add('hidden');
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

function showStats(count, fromCache) {
    elements.resultCount.textContent = count;
    elements.stats.classList.remove('hidden');
    
    if (fromCache) {
        elements.stats.textContent = `找到 ${count} 篇论文 (来自缓存)`;
    } else {
        elements.stats.textContent = `找到 ${count} 篇论文`;
    }
}

function hideStats() {
    elements.stats.classList.add('hidden');
}

// ==================== 两栏显示：发展脉络和季度汇总 ====================

function displayTrajectoryAndQuarterly(data) {
    const resultsContainer = document.getElementById('resultsContainer');
    
    if (!resultsContainer) return;
    
    // 显示容器
    resultsContainer.classList.remove('hidden');
    
    // 显示发展脉络总结（左栏）
    displayTrajectory(data.trajectory_summary);
    
    // 显示季度聚合（右栏）
    displayQuarterly(data.quarterly_data);
}

function displayTrajectory(trajectory) {
    const trajectoryContent = document.getElementById('trajectoryContent');
    
    if (!trajectoryContent) return;
    
    if (trajectory) {
        // 检查是否为有效文本
        if (typeof trajectory === 'string' && trajectory.trim().length > 0) {
            trajectoryContent.innerHTML = `<div style="line-height: 1.8; word-break: break-word;">${escapeHtml(trajectory)}</div>`;
        } else {
            trajectoryContent.innerHTML = `
                <div style="color: var(--text-light); text-align: center; padding: 2rem 1rem;">
                    <p>✨ 发展脉络总结生成中...</p>
                    <p style="font-size: 0.9rem; margin-top: 0.5rem;">AI正在分析论文数据，请稍候</p>
                </div>
            `;
        }
    } else {
        trajectoryContent.innerHTML = `
            <div style="color: var(--text-light); text-align: center; padding: 2rem 1rem;">
                <p>⚠️ 暂无发展脉络总结</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">请确保已启用AI总结功能或论文数据充分</p>
            </div>
        `;
    }
}

function displayQuarterly(quarterlyData) {
    const quarterlyContent = document.getElementById('quarterlyContent');
    
    if (!quarterlyContent) return;
    
    if (!quarterlyData || quarterlyData.length === 0) {
        quarterlyContent.innerHTML = `
            <div style="color: var(--text-light); text-align: center; padding: 2rem 1rem;">
                <p>📊 暂无季度数据</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem;">请尝试调整搜索条件</p>
            </div>
        `;
        return;
    }
    
    try {
        // 计算趋势（相邻季度的对比）
        let previousCount = null;
        const trendsMap = {};
        
        // 从后向前遍历（因为数据按时间倒序）
        for (let i = quarterlyData.length - 1; i >= 0; i--) {
            const current = quarterlyData[i];
            if (previousCount !== null) {
                const change = current.paper_count - previousCount;
                const trendPercent = Math.round((change / previousCount) * 100);
                trendsMap[current.quarter] = { change, trendPercent };
            }
            previousCount = current.paper_count;
        }
        
        // 生成季度卡片HTML
        const cardsHtml = quarterlyData.map((quarterly, index) => {
            const trend = trendsMap[quarterly.quarter];
            const trendIcon = trend ? (trend.change > 0 ? '📈' : trend.change < 0 ? '📉' : '➡️') : '';
            const trendText = trend ? ` ${trendIcon} ${Math.abs(trend.trendPercent)}%` : '';
            
            // 验证数据
            const paperCount = parseInt(quarterly.paper_count) || 0;
            const venues = Array.isArray(quarterly.top_venues) ? quarterly.top_venues : [];
            const titles = Array.isArray(quarterly.sample_titles) ? quarterly.sample_titles : [];
            
            return `
                <div class="quarterly-card">
                    <div class="quarterly-header">${escapeHtml(quarterly.quarter)}</div>
                    <div class="quarterly-stat">
                        <span>论文数: <strong>${paperCount}</strong>篇${trendText}</span>
                    </div>
                    ${venues.length > 0 ? `
                        <div class="quarterly-venues">
                            <strong>主要会议:</strong>
                            ${venues.map(v => `<span>${escapeHtml(v)}</span>`).join('')}
                        </div>
                    ` : ''}
                    ${titles.length > 0 ? `
                        <div style="font-size: 0.8rem; color: var(--text-light); margin-top: 0.5rem; padding-top: 0.5rem; border-top: 1px solid rgba(0,0,0,0.05);">
                            <strong style="display: block; margin-bottom: 0.3rem;">代表论文:</strong>
                            <ul style="margin: 0.3rem 0; padding-left: 1.2rem;">
                                ${titles.slice(0, 2).map(t => `
                                    <li style="font-size: 0.75rem; margin-bottom: 0.2rem;" title="${escapeHtml(t)}">${escapeHtml(t.substring(0, 50))}${t.length > 50 ? '...' : ''}</li>
                                `).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        quarterlyContent.innerHTML = cardsHtml;
    } catch (error) {
        console.error('Error displaying quarterly data:', error);
        quarterlyContent.innerHTML = `
            <div style="color: var(--text-light); text-align: center; padding: 2rem 1rem;">
                <p>❌ 显示季度数据时出错</p>
                <p style="font-size: 0.9rem; margin-top: 0.5rem; color: red;">${escapeHtml(error.message)}</p>
            </div>
        `;
    }
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
