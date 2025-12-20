document.addEventListener('DOMContentLoaded', () => {
    // ==========================================
    // 1. 全局变量与 DOM 元素获取
    // ==========================================
    let uploadedFilePath = null;
    let analysisData = null;
    let charts = {
        models: null,
        daily: null,
        hourly: null,
        language: null // ECharts instance
    };
    let currentPage = 0;

    // 页面元素
    const pages = {
        0: document.getElementById('pageUpload'),
        1: document.getElementById('page1'),
        2: document.getElementById('page2'),
        3: document.getElementById('page3'),
        4: document.getElementById('page4')
    };

    const loadingSection = document.getElementById('loadingSection');
    const errorSection = document.getElementById('errorSection');
    const prevArrow = document.getElementById('prevArrow');
    const nextArrow = document.getElementById('nextArrow');

    // 交互元素
    const fileInput = document.getElementById('fileInput');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileNameDisplay = document.getElementById('fileName');
    const retryBtn = document.getElementById('retryBtn');
    const exportBtn = document.getElementById('exportBtn');
    const restartBtn = document.getElementById('restartBtn');
if (prevArrow) prevArrow.addEventListener('click', () => changePage(-1));
if (nextArrow) nextArrow.addEventListener('click', () => changePage(1));

// 功能相关
if (retryBtn) retryBtn.addEventListener('click', resetUI);
if (restartBtn) restartBtn.addEventListener('click', resetUI);
if (exportBtn) exportBtn.addEventListener('click', exportPagesAsImages);
    // ==========================================
    // 2. 事件监听
    // ==========================================

    // 上传相关
// ==========================================
    // 2. 事件监听 & 3. 文件处理 (逻辑重构版)
    // ==========================================

    // 状态变量：用于存储用户先选中的厂商类型
    let currentProviderType = null;
    document.addEventListener('keydown', (e) => {
        // 如果还在上传页 (pageUpload 显示中)，则不响应键盘翻页
        if (pages[0].style.display !== 'none') return;

        // 如果正在显示错误页或加载页，也不响应
        if (errorSection.style.display !== 'none' || loadingSection.style.display !== 'none') return;

        if (e.key === 'ArrowUp') {
            // 模拟点击上一页 (或者直接调用 changePage)
            changePage(-1);
        } else if (e.key === 'ArrowDown') {
            // 模拟点击下一页
            changePage(1);
        }
    });
    // 获取弹窗相关元素
    const providerModal = document.getElementById('providerModal');
    const cancelProviderBtn = document.getElementById('cancelProviderBtn');
    const providerBtns = document.querySelectorAll('.provider-btn');

    // --- A. 点击“上传 JSON 记录”按钮 -> 显示厂商选择弹窗 ---
    uploadBtn.addEventListener('click', () => {
        // 重置状态
        currentProviderType = null;
        fileInput.value = ''; 
        // 显示弹窗
        providerModal.style.display = 'flex';
    });

    // --- B. 弹窗中点击“取消” ---
    if (cancelProviderBtn) {
        cancelProviderBtn.addEventListener('click', () => {
            providerModal.style.display = 'none';
        });
    }

    // --- C. 弹窗中选择具体厂商 -> 记录类型 -> 触发文件选择 ---
    providerBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            // 1. 获取并保存厂商类型
            currentProviderType = e.target.dataset.type;
            
            // 2. 隐藏弹窗
            providerModal.style.display = 'none';

            // 3. 自动触发文件选择框 (这是关键一步)
            // 用户在选完厂商后，浏览器会立即弹出文件选择窗口
            fileInput.click();
        });
    });

    // --- D. 文件选择完毕 -> 携带厂商信息上传 ---
    fileInput.addEventListener('change', handleFileSelect);

    function handleFileSelect(event) {
        const file = event.target.files[0];
        // 如果用户在文件选择框点了“取消”，file 就是 undefined，直接返回即可
        if (!file) return;

        // 校验文件格式
        if (!file.name.endsWith('.json')) {
            showError('请选择 .json 格式的文件');
            return;
        }

        // 安全校验：确保有厂商类型（理论上流程是对的，这里防一手）
        if (!currentProviderType) {
            showError('未选择厂商，请重新上传');
            return;
        }

        fileNameDisplay.textContent = `✓ ${file.name} (${currentProviderType})`;
        
        // 立即开始上传
        uploadFile(file, currentProviderType);
    }

    function uploadFile(file, providerType) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('provider_type', providerType); // 关键：后端需要这个字段

        showLoading(true);

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) throw new Error(data.error);
            uploadedFilePath = data.filepath;
            analyzeData();
        })
        .catch(error => {
            showError('上传失败: ' + error.message);
            // 出错后清空状态，允许重试
            fileInput.value = '';
            currentProviderType = null;
        });
    }
    function analyzeData() {
fetch('/api/analyze', {
method: 'POST',
headers: { 'Content-Type': 'application/json' },
body: JSON.stringify({ filepath: uploadedFilePath })
})
.then(response => response.json())
.then(data => {
if (data.error) throw new Error(data.error);
analysisData = data;
// 确保数据加载完后有短暂延迟，体验更流畅
setTimeout(() => {
displayResults();
}, 500);
})
.catch(error => {
showError('分析失败: ' + error.message);
});
}

    // (analyzeData 函数保持不变...)
    // ==========================================
    // 4. 页面渲染与逻辑核心
    // ==========================================

    function displayResults() {
        showLoading(false);
        errorSection.style.display = 'none';

        // 设置背景主题
        setBackgroundTheme();

        // --- 第一页填充 ---
        updateOverviewCards();
        createDailyChart();
        generateMonthCopy();
        generateCharactersCopy();
        generateSessionsCopy();

        // --- 第二页填充 ---
        createModelsChart();
        createLanguageChart();
        generateModelsCopy();

        // --- 第三页填充 ---
        createHourlyChart();
        createTimeStats();
        generateHourlyCopy();
        generateTimeCopy();

        // --- 第四页填充 ---
        generatePolitenessSummary();
        generateRefuseCopy();
        createEmojiList();
        generateEmojiCopy();

        // 进入第一页
        showPage(1);
    }

    // 设置背景主题
    function setBackgroundTheme() {
        const hourly = analysisData?.per_hour_distribution || {};
        console.log("analysis data:", analysisData);
        // 找出最活跃的小时，默认为 12 点
        let peakHour = '12';
        if (Object.keys(hourly).length > 0) {
            peakHour = Object.keys(hourly).reduce((a, b) => hourly[b] > (hourly[a] || 0) ? b : a);
        }

        const h = parseInt(peakHour, 10);
        const body = document.body;

        // 移除旧类
        body.classList.remove('theme-morning', 'theme-dusk', 'theme-night', 'theme-day');

        if (h >= 5 && h <= 11) {
            body.classList.add('theme-morning');
        } else if (h >= 16 && h <= 19) {
            body.classList.add('theme-dusk');
        } else if (h >= 20 || h <= 4) {
            body.classList.add('theme-night');
        } else {
            body.classList.add('theme-day');
        }
    }

    // ==========================================
    // 5. 导航逻辑
    // ==========================================

    function changePage(delta) {
        const target = currentPage + delta;
        if (target >= 1 && target <= 4) {
            showPage(target);
        }
    }

    function showPage(n) {
        // 隐藏所有页面
        Object.values(pages).forEach(p => {
            if (p) {
                p.style.display = 'none';
                p.classList.remove('active');
            }
        });

        // 显示目标页面
        const targetPage = pages[n];
        if (targetPage) {
            targetPage.style.display = 'flex'; // 使用 flex 布局居中
            // 强制重绘触发动画
            void targetPage.offsetWidth;
            targetPage.classList.add('active');
        }

        currentPage = n;

        // 控制箭头显示
        if (prevArrow) prevArrow.style.display = (n > 1) ? 'flex' : 'none';
        if (nextArrow) nextArrow.style.display = (n > 0 && n < 4) ? 'flex' : 'none';

        // 特殊处理：如果是第二页，ECharts 需要 resize
        if (n === 2 && charts.language) {
            setTimeout(() => {
                charts.language.resize();
            }, 100);
        }
    }

    function showLoading(show) {
        // 隐藏上传页
        pages[0].style.display = 'none';
        if (show) {
            loadingSection.style.display = 'flex';
            errorSection.style.display = 'none';
        } else {
            loadingSection.style.display = 'none';
        }
    }

    function showError(msg) {
        showLoading(false);
        Object.values(pages).forEach(p => p.style.display = 'none');
        errorSection.style.display = 'flex';
        document.getElementById('errorMessage').textContent = msg;
    }

    function resetUI() {
        uploadedFilePath = null;
        analysisData = null;
        fileInput.value = '';
        fileNameDisplay.textContent = '';

        // 销毁图表
        if (charts.models) charts.models.destroy();
        if (charts.daily) charts.daily.destroy();
        if (charts.hourly) charts.hourly.destroy();
        charts.models = null; 

        if (charts.language && typeof charts.language.dispose === 'function') {
            charts.language.dispose();
        }
        charts.language = null;
        document.getElementById('languageChart').innerHTML = '';

        // 【新增】尝试恢复 Page 2 的原始结构 (可选，但推荐)
        // 这样下次上传文件时，createModelsChart 面对的是一个干净的或者原始的容器
        const p2Container = document.querySelector('#page2 .chart-container-row');
        if (p2Container) {
             p2Container.innerHTML = ''; // 清空即可，下次 createModelsChart 会重建
        }

        errorSection.style.display = 'none';
        showPage(0); // 回到上传页
    }

    // ==========================================
    // 6. 图表绘制函数
    // ==========================================

    // 第一页：每日趋势
// ==========================================
    // 6. 图表绘制函数 (紧凑布局优化版)
    // ==========================================

    // 第一页：每日趋势 (已修复：显示坐标轴，自适应高度)
// 第一页：每日趋势 (升级版：横向滚动 + 自动定位最忙月份)
    function createDailyChart() {
        const chatDaysData = analysisData.chat_days || [];
        if (chatDaysData.length === 0) return;

        // 1. 数据准备：使用所有数据，不再切片
        // 确保按日期排序
        chatDaysData.sort((a, b) => new Date(a.date) - new Date(b.date));

        const dates = chatDaysData.map(item => item.date.substring(5)); // "MM-DD"
        const counts = chatDaysData.map(item => parseInt(item.counts || 0));

        // 2. 算法：寻找“最活跃月份”的起始位置 (用于默认滚动定位)
        const monthMap = {};
        let maxCount = -1;
        let bestMonthPrefix = '';

        chatDaysData.forEach((item, index) => {
            const m = item.date.substring(0, 7); // YYYY-MM
            if (!monthMap[m]) monthMap[m] = { total: 0, startIndex: index };
            monthMap[m].total += (item.counts || 0);

            if (monthMap[m].total > maxCount) {
                maxCount = monthMap[m].total;
                bestMonthPrefix = m;
            }
        });

        // 获取最活跃月份的第一天在数组中的索引
        const scrollTargetIndex = bestMonthPrefix ? monthMap[bestMonthPrefix].startIndex : 0;

        // 3. DOM 改造：创建滚动容器
        const canvas = document.getElementById('dailyChart');
        const chartBox = canvas.parentElement;

        // 检查是否已经创建了 wrapper，防止重复嵌套
        let wrapper = document.getElementById('dailyChartWrapper');
        if (!wrapper) {
            wrapper = document.createElement('div');
            wrapper.id = 'dailyChartWrapper';
            wrapper.style.height = '100%';
            wrapper.style.position = 'relative';

            // 将 canvas 移动到 wrapper 内部
            chartBox.appendChild(wrapper);
            wrapper.appendChild(canvas);

            // 设置父容器样式以支持横向滚动
            chartBox.style.overflowX = 'auto';
            chartBox.style.overflowY = 'hidden';
            chartBox.style.webkitOverflowScrolling = 'touch'; // 移动端顺滑滚动

            // 隐藏滚动条 (Firefox)
            chartBox.style.scrollbarWidth = 'none';
        }

        // 4. 动态计算图表宽度
        // 逻辑：屏幕(容器)宽度对应显示 30 天的数据密度
        const visibleDays = 30;
        const containerWidth = chartBox.clientWidth || 350; // 获取当前屏幕宽度
        const pixelPerDay = containerWidth / visibleDays;   // 每一天占多少像素

        // 总宽度 = 总天数 * 单天宽度 (如果总天数少于30天，则撑满屏幕即可)
        const totalWidth = Math.max(containerWidth, dates.length * pixelPerDay);

        // 强制设置 wrapper 宽度，撑开滚动区域
        wrapper.style.width = `${totalWidth}px`;

        // 5. 绘制图表
        const ctx = canvas.getContext('2d');
        if (charts.daily) charts.daily.destroy();

        charts.daily = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: '对话数',
                    data: counts,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 3,
                    pointBackgroundColor: '#fff',
                    pointBorderColor: '#667eea'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 必须为 false 才能适应动态宽度
                plugins: {
                    legend: { display: false },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: {
                        display: true,
                        grid: { display: false },
                        ticks: {
                            font: { size: 10 },
                            maxRotation: 0,
                            autoSkip: true, // 让 Chart.js 自动决定标签密度
                            maxTicksLimit: dates.length // 取消之前的限制，因为现在宽度够大
                        }
                    },
                    y: {
                        display: true,
                        border: { display: false },
                        grid: { color: '#f0f0f0' },
                        ticks: {
                            font: { size: 9 },
                            maxTicksLimit: 4
                        }
                    }
                },
                layout: { padding: 0 }
            }
        });

        // 6. 自动滚动到最活跃的月份
        // 使用 setTimeout 确保 DOM 渲染完成后执行滚动
        setTimeout(() => {
            const scrollPos = scrollTargetIndex * pixelPerDay;
            // 平滑滚动可能在初始化时有点晕，直接跳转更利索
            chartBox.scrollLeft = scrollPos;
        }, 100);
    }

    // 第二页：模型分布 (紧凑版)
  // 第二页：模型分布 (横向堆叠条形图版)
  // 第二页：模型分布 (GitHub 风格 HTML 复刻版)
// 第二页：模型分布 (GitHub 风格 - 适配现有 HTML)
    function createModelsChart() {
        const modelsData = analysisData.most_used_models || [];
        
        // 1. 排序
        modelsData.sort((a, b) => parseInt(b.usage) - parseInt(a.usage));

        // 2. GitHub 风格色盘
       const colors = [
            '#667eea', // 主题紫 (Primary)
            '#4facfe', // 亮空蓝 (Blue)
            '#f093fb', // 糖果粉 (Pink)
            '#43e97b', // 薄荷绿 (Green)
            '#fa709a', // 珊瑚红 (Red-ish)
            '#a18cd1', // 薰衣草 (Light Purple)
            '#ffcc33', // 暖阳黄 (Yellow)
            '#00c6fb'  // 青色 (Cyan)
        ];

        const totalUsage = modelsData.reduce((sum, item) => sum + parseInt(item.usage), 0);

        // 3. 【关键修正】获取你 HTML 中实际存在的容器
        // 你的 HTML 结构是 <div class="chart-container-row">
        const container = document.querySelector('#page2 .chart-container-row');
        
        if (!container) return; // 安全检查

        // 4. 重置容器样式 (覆盖原来的 Flex 左右布局，改为上下堆叠)
        container.style.display = 'block'; 
        container.style.height = 'auto';
        container.innerHTML = ''; // 清空原本的 Canvas 和 text-half

        // 5. 创建进度条 (The Bar)
        const progressBar = document.createElement('div');
        progressBar.className = 'github-progress-bar';

        // 6. 创建图例区域 (The Legend)
        const legendContainer = document.createElement('div');
        legendContainer.className = 'github-legend-container';

        // 7. 生成数据 DOM
        modelsData.forEach((item, index) => {
            const usage = parseInt(item.usage);
            const percent = ((usage / totalUsage) * 100);
            const displayPercent = percent.toFixed(1) + '%';
            const simpleName = item.model.replace('deepseek-', '').replace('gpt-', '').replace('claude-', '');
            const color = colors[index % colors.length];

            // 只有大于 0 的才显示在进度条里
            if (percent > 0) {
                const segment = document.createElement('div');
                segment.className = 'github-bar-segment';
                segment.style.backgroundColor = color;
                segment.style.width = '0%'; // 初始 0，用于动画
                segment.dataset.width = percent + '%';
                progressBar.appendChild(segment);
            }

            // 图例全部显示
            const legendItem = document.createElement('div');
            legendItem.className = 'github-legend-item';
            legendItem.innerHTML = `
                <div class="github-legend-dot" style="background-color: ${color}"></div>
                <span>${simpleName}</span>
                <span class="github-legend-percent">${displayPercent}</span>
            `;
            legendContainer.appendChild(legendItem);
        });

        // 8. 重建文案区域 (因为原有的被 innerHTML='' 删掉了)
        const copyBox = document.createElement('div');
        copyBox.id = 'modelsCopy'; // 恢复 ID，供 generateModelsCopy 使用
        copyBox.className = 'models-text-below'; 
        
        // 【新增】因为现在是 block 布局，手动加一点上边距，让它离图例远一点，呼吸感更好
        copyBox.style.marginTop = '20px';
        // 9. 组装 DOM
        container.appendChild(progressBar);
        container.appendChild(legendContainer);
        container.appendChild(copyBox);

        // 10. 触发动画
        setTimeout(() => {
            const segments = progressBar.querySelectorAll('.github-bar-segment');
            segments.forEach(seg => {
                seg.style.width = seg.dataset.width;
            });
        }, 100);

        // 11. 重新生成文案 (必须在 copyBox 被添加到 DOM 后调用)
        generateModelsCopy();
    }
   // ==========================================
    // 第二页：语言分布 (带切换功能 + 静态文案)
    // ==========================================
    function createLanguageChart() {
        const languageData = analysisData.most_used_language || [];
        const container = document.getElementById('languageChart');
        const copyBox = document.getElementById('languageCopy'); 
        
        // 1. 清空容器
        if (charts.language && typeof charts.language.dispose === 'function') {
            charts.language.dispose();
            charts.language = null;
        }
        container.innerHTML = ''; 
        container.className = 'apple-chart-container';
        container.style.height = 'auto';

        // 2. 数据分类
        const codeData = languageData.filter(d => d.type === 'code');
        const naturalData = languageData.filter(d => d.type === 'natural');

        // 3. 【核心修改】预先生成文案，确保本次查看期间文案不会变
        // 这样无论怎么切换，显示的都是同一段话
        const staticCodeCopy = CopyWriter.getCodeCopy(codeData);
        const staticNaturalCopy = CopyWriter.getNaturalCopy(naturalData);

        // 4. 创建切换按钮 UI
        const toggleWrapper = document.createElement('div');
        toggleWrapper.className = 'lang-toggle-wrapper';
        toggleWrapper.innerHTML = `
            <div class="lang-toggle">
                <button class="lang-btn active" data-type="code">编程语言</button>
                <button class="lang-btn" data-type="natural">自然语言</button>
            </div>
        `;
        container.appendChild(toggleWrapper);

        // 5. 创建列表容器
        const listWrapper = document.createElement('div');
        listWrapper.className = 'lang-list-wrapper';
        container.appendChild(listWrapper);

        // 6. 核心渲染函数
        function renderList(type) {
            // 列表淡出
            listWrapper.style.opacity = '0.5';
            copyBox.style.opacity = '0.5'; 
            
            setTimeout(() => {
                listWrapper.innerHTML = ''; // 清空列表
                
                // A. 决定使用哪组数据
                const data = type === 'code' ? codeData : naturalData;
                
                // B. 【核心修改】使用预先生成的静态文案
                if (type === 'code') {
                    copyBox.innerHTML = staticCodeCopy;
                } else {
                    copyBox.innerHTML = staticNaturalCopy;
                }
                copyBox.style.opacity = '1'; 

                // C. 渲染图表条目
                const sorted = data
                    .sort((a, b) => parseInt(b.counts) - parseInt(a.counts))
                    .slice(0, 4); 

                if (sorted.length === 0) {
                    listWrapper.innerHTML = '<div style="text-align:center;color:#999;padding:30px;">暂无数据</div>';
                    listWrapper.style.opacity = '1';
                    return;
                }

                const maxCount = parseInt(sorted[0].counts);

                sorted.forEach((item, index) => {
                    const count = parseInt(item.counts);
                    const percent = (count / maxCount) * 100;
                    
                    let displayName = item.language;
                    if (displayName === 'else') displayName = 'English / Other';
                    if (displayName === 'chinese') displayName = '中文';
                    if (displayName === 'cpp') displayName = 'C++';
                    if (displayName === 'c') displayName = 'C';

                    const group = document.createElement('div');
                    group.className = 'apple-bar-group';
                    // 动画
                    group.style.animation = 'none';
                    group.offsetHeight; 
                    group.style.animation = `fadeSlideIn 0.5s forwards ${index * 0.05}s`;
                    group.style.opacity = '0';

                    group.innerHTML = `
                        <div class="apple-bar-header">
                            <span class="apple-bar-label">${displayName}</span>
                            <span class="apple-bar-value">${formatNumber(count)}</span>
                        </div>
                        <div class="apple-track">
                            <div class="apple-fill" style="width: 0%" data-width="${percent}%"></div>
                        </div>
                    `;
                    listWrapper.appendChild(group);
                });

                // 恢复列表透明度
                listWrapper.style.opacity = '1';

                // 触发进度条动画
                requestAnimationFrame(() => {
                    const bars = listWrapper.querySelectorAll('.apple-fill');
                    bars.forEach(bar => {
                        bar.style.width = bar.getAttribute('data-width');
                    });
                });
            }, 150);
        }

        // 7. 绑定点击事件
        const btns = toggleWrapper.querySelectorAll('.lang-btn');
        btns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                btns.forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                renderList(e.target.dataset.type);
            });
        });

        // 8. 初始渲染
        renderList('code');
    }
     function createHourlyChart() {
        const hourlyData = analysisData.per_hour_distribution || {};
        const hours = Object.keys(hourlyData).sort((a, b) => parseInt(a) - parseInt(b));
        const values = hours.map(h => hourlyData[h]);

        // 补全 0-23 小时
        const fullHours = [];
        const fullValues = [];
        for (let i = 0; i < 24; i++) {
            const hStr = i.toString();
            fullHours.push(i + '点');
            fullValues.push(hourlyData[hStr] || 0);
        }

        const ctx = document.getElementById('hourlyChart').getContext('2d');
        if (charts.hourly) charts.hourly.destroy();

        // 更丰富的紫色渐变
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(0.5, '#8b5cf6');
        gradient.addColorStop(1, '#764ba2');

        charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: fullHours,
                datasets: [{
                    label: '对话次数',
                    data: fullValues,
                    backgroundColor: gradient,
                    borderRadius: 6,
                    barPercentage: 0.7,
                    hoverBackgroundColor: '#764ba2',
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                return `时间: ${context[0].label}`;
                            },
                            label: function(context) {
                                return `对话次数: ${context.parsed.y}`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: {
                            color: '#666',
                            font: { size: 11, weight: '500' },
                            maxRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 12
                        }
                    },
                    y: {
                        display: true,
                        beginAtZero: true,
                        border: { display: false },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#666',
                            font: { size: 11, weight: '500' },
                            maxTicksLimit: 6,
                            padding: 8
                        }
                    }
                },
                layout: {
                    padding: {
                        top: 20,
                        bottom: 10,
                        left: 10,
                        right: 10
                    }
                },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart',
                    delay: (context) => {
                        let delay = 0;
                        if (context.type === 'data' && context.mode === 'default') {
                            delay = context.dataIndex * 50;
                        }
                        return delay;
                    }
                }
            }
        });
    }
    // ==========================================
    // 7. 文案生成逻辑 (你的核心创意)
    // ==========================================

    function pickOne(arr) { return arr[Math.floor(Math.random() * arr.length)]; }
    function formatNumber(num) {
        if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
        return num.toString();
    }

    // 第一页内容
  // ==========================================
    // 修改函数 1: updateOverviewCards
    // ==========================================
    function updateOverviewCards() {
        // 1. 更新会话数
        document.getElementById('sessionCount').textContent = analysisData.session_count?.session_count || 0;

        // 2. 更新字数 (区分用户与 AI)
        const totalCharsData = analysisData.total_characters || [];

        let userTotal = 0;
        let aiTotal = 0;

        totalCharsData.forEach(item => {
            const count = parseInt(item.counts || 0);
            const type = item.model_type || '';

            // 逻辑：只要是以 _REQUEST 结尾的，都算作用户输入
            if (type.endsWith('_REQUEST')) {
                userTotal += count;
            } else {
                // 包括 _RESPONSE 和 _THINK，都算作 AI 生成
                aiTotal += count;
            }
        });

        // 更新 HTML 元素
        const userEl = document.getElementById('userChars');
        const aiEl = document.getElementById('aiChars');

        // 只有当元素存在时才更新 (防止报错)
        if (userEl) userEl.textContent = formatNumber(userTotal);
        if (aiEl) aiEl.textContent = formatNumber(aiTotal);
    }

    function createTimeStats() {
        const timeData = analysisData.time_limit || [];
        let earliest = null, latest = null;
        timeData.forEach(item => {
            if (item.earliest_time) earliest = item.earliest_time;
            if (item.latest_time) latest = item.latest_time;
        });

        const container = document.getElementById('timeStats');
        container.innerHTML = '';

        if (earliest) {
            container.innerHTML += `
                <div class="stat-row">
                    <span>🌅 最早一次</span>
                    <strong>${earliest}</strong>
                </div>`;
        }
        if (latest) {
            container.innerHTML += `
                <div class="stat-row">
                    <span>🌃 最晚一次</span>
                    <strong>${latest}</strong>
                </div>`;
        }
    }
    // ==========================================
    // 7. 文案生成逻辑 (重构版：调用 CopyWriter)
    // ==========================================

    // 辅助函数 pickOne 可以删掉了，CopyWriter 内部有了

    function formatNumber(num) {
        return CopyWriter.formatNumber(num);
    }

    // 第一页：字数文案
    function generateCharactersCopy() {
        const totalCharsData = analysisData.total_characters || [];
        let grandTotal = 0;
        let aiTotal = 0;
        let userTotal = 0;

        totalCharsData.forEach(item => {
            const count = parseInt(item.counts || 0);
            grandTotal += count;
            if (item.model_type.endsWith('_REQUEST')) {
                userTotal += count;
            } else {
                aiTotal += count;
            }
        });

        // 调用 CopyWriter
        const text = CopyWriter.getCharactersCopy(userTotal, aiTotal);
        document.getElementById('charactersCopy').textContent = text;
    }

    // 第一页：月份文案
    function generateMonthCopy() {
        const chatDaysData = analysisData.chat_days || [];
        if (!chatDaysData.length) return;

        const monthCounts = {};
        chatDaysData.forEach(({ date, counts }) => {
            const m = new Date(date).getMonth() + 1;
            monthCounts[m] = (monthCounts[m] || 0) + parseInt(counts || 0);
        });

        const topMonth = Object.keys(monthCounts).sort((a, b) => monthCounts[b] - monthCounts[a])[0];
        
        // 调用 CopyWriter
        const html = CopyWriter.getMonthCopy(topMonth, monthCounts[topMonth]);
        document.getElementById('monthCopy').innerHTML = html;
    }

    // 第一页：会话文案
    function generateSessionsCopy() {
        const count = analysisData.session_count?.session_count || 0;
        // 调用 CopyWriter
        const text = CopyWriter.getSessionsCopy(count);
        document.getElementById('sessionsCopy').textContent = text;
    }

    // 第二页：模型文案
    function generateModelsCopy() {
        const models = analysisData.most_used_models || [];
        const topModel = models.length > 0 ? models[0].model : '';
        // 调用 CopyWriter
        const html = CopyWriter.getModelsCopy(topModel);
        document.getElementById('modelsCopy').innerHTML = html;
    }

    // 第二页：语言文案


    // 第三页：小时文案
    function generateHourlyCopy() {
        const hourly = analysisData.per_hour_distribution || {};
        // 调用 CopyWriter
        const text = CopyWriter.getHourlyCopy(hourly);
        document.getElementById('hourlyCopy').textContent = text;
    }

    // 第三页：时间统计 (保持不变，只是格式化时间)
    function generateTimeCopy() {
        const box = document.getElementById('timeCopy');
        // 这里也可以加随机文案，例如
        const texts = [
            '时间记录着思考的轨迹，每一分钟都没有被辜负。',
            '这些时刻，是你与未来对话的证据。',
            '跨越昼夜的记录，见证了求知的渴望。'
        ];
        // 简单随机一个
        box.textContent = texts[Math.floor(Math.random() * texts.length)];
    }

    // 第四页：礼貌文案
    function generatePolitenessSummary() {
        const list = analysisData.polite_extent || [];
        const politeWords = ['您', '请', '谢谢', '麻烦'];
        const impoliteWords = ['滚', '垃圾', '闭嘴'];

        let pCount = 0, iCount = 0;
        list.forEach(item => {
            if (politeWords.some(w => item.word.includes(w))) pCount += parseInt(item.counts);
            if (impoliteWords.some(w => item.word.includes(w))) iCount += parseInt(item.counts);
        });

        document.getElementById('politeness').textContent = pCount;

        const total = pCount + iCount;
        const ratio = total ? (pCount / total) : 1;

        // 调用 CopyWriter
        const text = CopyWriter.getPolitenessCopy(ratio);
        document.getElementById('politenessSummary').textContent = text;
    }

    // 第四页：拒绝文案
    function generateRefuseCopy() {
        const count = analysisData.refuse_counts || 0;
        document.getElementById('refuseCount').textContent = count;
        // 调用 CopyWriter
        const text = CopyWriter.getRefuseCopy(count);
        document.getElementById('refuseCopy').textContent = text;
    }

    // 第四页：Emoji 文案
    function generateEmojiCopy() {
        const emojis = analysisData.emoji_counts || [];
        const total = emojis.reduce((s, i) => s + parseInt(i.counts), 0);
        // 调用 CopyWriter
        const text = CopyWriter.getEmojiCopy(total);
        document.getElementById('emojiCopy').textContent = text;
    }
    function createEmojiList() {
        const emojis = analysisData.emoji_counts || [];
        const container = document.getElementById('emojiList');
        container.innerHTML = '';

        // 取前10个
        emojis.sort((a, b) => b.counts - a.counts).slice(0, 10).forEach(e => {
            const div = document.createElement('div');
            div.className = 'emoji-item';
            div.innerHTML = `<span class="emoji-char">${e.emoji}</span> ${e.counts}`;
            container.appendChild(div);
        });
    }

    function generateEmojiCopy() {
        const emojis = analysisData.emoji_counts || [];
        const total = emojis.reduce((s, i) => s + parseInt(i.counts), 0);
        const box = document.getElementById('emojiCopy');

        if (total > 100) box.textContent = '表情包达人！你的情绪表达细腻丰富，让对话充满生机。';
        else if (total > 0) box.textContent = '适度使用表情，恰到好处地为文字增色。';
        else box.textContent = '冷静克制，你更习惯用纯粹的文字传递思想。';
    }
// ==========================================
    // 8. 导出功能 (终极修复：尺寸统一 + 进度条暴力渲染)
    // ==========================================
// ==========================================
    // 8. 导出功能 (终极修复：显示语言条 + 紧凑高度)
    // ==========================================
// ==========================================
    // 8. 导出功能 (完美修复：统一高度 + 颜色保留)
    // ==========================================

    async function exportPagesAsImages() {
        if (!window.html2canvas) {
            alert('导出模块加载中，请稍后再试...');
            return;
        }

        const actionArea = document.querySelector('.action-area');
        const navArrows = document.querySelector('.nav-arrows');
        
        // 1. 临时隐藏 UI
        if (actionArea) actionArea.style.visibility = 'hidden';
        if (navArrows) navArrows.style.display = 'none';

        // 2. 准备离屏容器
        let offScreenContainer = document.getElementById('exportContainer');
        if (!offScreenContainer) {
            offScreenContainer = document.createElement('div');
            offScreenContainer.id = 'exportContainer';
            document.body.appendChild(offScreenContainer);
        }
        offScreenContainer.innerHTML = '';

        const exportPageIndices = [1, 2, 3, 4];

        try {
            for (let i of exportPageIndices) {
                const originalPage = document.getElementById(`page${i}`);
                const originalCard = originalPage.querySelector('.card-container');
                if (!originalCard) continue;

                // --- A. 克隆与布局环境搭建 ---
                const clonedCard = originalCard.cloneNode(true);
                
                const wrapper = document.createElement('div');
                wrapper.style.position = 'absolute';
                wrapper.style.top = '0';
                wrapper.style.left = '0';
                wrapper.style.width = '420px'; // 模拟手机宽度
                wrapper.style.padding = '20px';
                wrapper.style.display = 'flex';
                wrapper.style.justifyContent = 'center';
                wrapper.appendChild(clonedCard);
                offScreenContainer.appendChild(wrapper);

                // --- B. 样式冻结与统一 ---
                
                clonedCard.classList.add('no-animation');
                
                // 1. 【修复高度不一】设定统一的最小高度，保证所有卡片看起来一样高
                clonedCard.style.height = 'auto'; 
                clonedCard.style.minHeight = '480px'; // 设定一个标准高度
                clonedCard.style.maxHeight = 'none'; 
                clonedCard.style.overflow = 'visible';
                
                // 使用 Flex 布局让内容垂直分布，避免 Page 3 下方出现大片死板的空白
                clonedCard.style.display = 'flex';
                clonedCard.style.flexDirection = 'column';
                clonedCard.style.justifyContent = 'space-between'; // 关键：内容分散对齐
                
                clonedCard.style.width = '100%'; 
                clonedCard.style.background = '#ffffff';
                clonedCard.style.boxShadow = 'none';
                clonedCard.style.margin = '0';

                // 2. 【修复 Page 2 语言条消失】
                const appleGroups = clonedCard.querySelectorAll('.apple-bar-group');
                appleGroups.forEach(group => {
                    group.style.opacity = '1';
                    group.style.animation = 'none';
                });

                // 3. 修复 Apple Track
                const appleTracks = clonedCard.querySelectorAll('.apple-track');
                appleTracks.forEach(track => {
                    track.style.width = '100%';
                    track.style.display = 'block';
                    track.style.height = '10px';
                    track.style.background = 'rgba(0,0,0,0.06)';
                });

                // 4. 【修复 Page 2 条形图无颜色】
                const progressBars = clonedCard.querySelectorAll('.github-bar-segment, .apple-fill');
                progressBars.forEach(bar => {
                    const finalWidth = bar.getAttribute('data-width');
                    // 【关键】先获取原本的背景色（GitHub 条形图是内联样式的颜色）
                    const originalColor = bar.style.backgroundColor;

                    if (finalWidth) {
                        // 重新写回样式时，显式带上 background-color
                        bar.style.cssText = `
                            width: ${finalWidth} !important;
                            background-color: ${originalColor} !important; 
                            transition: none !important;
                            animation: none !important;
                            display: block !important;
                            height: 100% !important;
                        `;
                        
                        // Apple Bar 特殊处理（它是渐变色）
                        if (bar.classList.contains('apple-fill')) {
                            bar.style.background = 'linear-gradient(90deg, #667eea, #764ba2)';
                            bar.style.borderRadius = '10px';
                        }
                    }
                });

                // 5. 修复 Canvas 内容
                const originalCanvases = originalCard.querySelectorAll('canvas');
                const clonedCanvases = clonedCard.querySelectorAll('canvas');
                originalCanvases.forEach((orig, index) => {
                    if (clonedCanvases[index]) {
                        const dest = clonedCanvases[index];
                        dest.width = orig.width;
                        dest.height = orig.height;
                        dest.style.width = '100%';
                        dest.style.height = orig.style.height || 'auto';
                        const ctx = dest.getContext('2d');
                        ctx.drawImage(orig, 0, 0);
                    }
                });

                // --- C. 截图 ---
                void clonedCard.offsetWidth;
                await new Promise(resolve => setTimeout(resolve, 300));

                const cardCanvas = await html2canvas(clonedCard, {
                    scale: 3, 
                    useCORS: true,
                    backgroundColor: '#ffffff',
                    logging: false
                });

                // --- D. 合成背景 ---
                const finalCanvas = document.createElement('canvas');
                const width = 1080;
                const height = 1920;
                finalCanvas.width = width;
                finalCanvas.height = height;
                const ctx = finalCanvas.getContext('2d');

                // 绘制背景
                const gradient = ctx.createLinearGradient(0, 0, width, height);
                if (document.body.classList.contains('theme-night')) {
                    gradient.addColorStop(0, '#30cfd0');
                    gradient.addColorStop(1, '#330867');
                } else if (document.body.classList.contains('theme-dusk')) {
                    gradient.addColorStop(0, '#fa709a');
                    gradient.addColorStop(1, '#fee140');
                } else if (document.body.classList.contains('theme-morning')) {
                    gradient.addColorStop(0, '#a18cd1');
                    gradient.addColorStop(1, '#fbc2eb');
                } else {
                    gradient.addColorStop(0, '#84fab0');
                    gradient.addColorStop(1, '#8fd3f4');
                }
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, width, height);

                // 绘制卡片 (垂直居中)
                const cardAspect = cardCanvas.width / cardCanvas.height;
                const drawWidth = width * 0.85; 
                const drawHeight = drawWidth / cardAspect;
                const drawX = (width - drawWidth) / 2;
                const drawY = (height - drawHeight) / 2;

                ctx.save();
                ctx.shadowColor = "rgba(0, 0, 0, 0.25)";
                ctx.shadowBlur = 60;
                ctx.shadowOffsetY = 30;
                ctx.drawImage(cardCanvas, drawX, drawY, drawWidth, drawHeight);
                ctx.restore();

                // --- E. 下载 ---
                const link = document.createElement('a');
                link.download = `AI_Memory_2025_Page_${i}.png`;
                link.href = finalCanvas.toDataURL('image/png');
                link.click();
                
                offScreenContainer.innerHTML = '';
            }
        } catch (err) {
            console.error('导出失败:', err);
            alert('导出遇到问题，请重试');
        } finally {
            if (actionArea) actionArea.style.visibility = 'visible';
            if (navArrows) navArrows.style.display = 'flex';
            if (offScreenContainer) offScreenContainer.innerHTML = '';
            
            alert('导出完成！');
        }
    }
});