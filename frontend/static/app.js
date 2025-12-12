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

    // ==========================================
    // 2. 事件监听
    // ==========================================
    
    // 上传相关
    uploadBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);
    
    // 导航相关
    if (prevArrow) prevArrow.addEventListener('click', () => changePage(-1));
    if (nextArrow) nextArrow.addEventListener('click', () => changePage(1));
    
    // 功能相关
    if (retryBtn) retryBtn.addEventListener('click', resetUI);
    if (restartBtn) restartBtn.addEventListener('click', resetUI);
    if (exportBtn) exportBtn.addEventListener('click', exportPagesAsImages);

    // 窗口调整时重绘 ECharts
    window.addEventListener('resize', () => {
        if (charts.language) charts.language.resize();
    });

    // ==========================================
    // 3. 文件处理与 API 通信
    // ==========================================

    function handleFileSelect(event) {
        const file = event.target.files[0];
        if (!file) return;

        if (!file.name.endsWith('.json')) {
            showError('请选择 .json 格式的文件');
            return;
        }

        fileNameDisplay.textContent = `✓ ${file.name}`;
        uploadFile(file);
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

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
        generateLanguageCopy();

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
        if (charts.language) {
            charts.language.dispose();
            charts.language = null;
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
    function createModelsChart() {
        const modelsData = analysisData.most_used_models || [];
        const labels = modelsData.map(item => item.model.replace('deepseek-', '')); // 简化名字
        const data = modelsData.map(item => parseInt(item.usage || 0));

        const ctx = document.getElementById('modelsChart').getContext('2d');
        if (charts.models) charts.models.destroy();

        charts.models = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b'],
                    borderWidth: 1,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // 【关键】
                cutout: '60%', // 环稍微细一点
                plugins: {
                    legend: { 
                        position: 'right', // 放在右侧节省垂直空间
                        labels: { 
                            boxWidth: 8, 
                            font: { size: 10 },
                            padding: 10
                        } 
                    }
                },
                layout: { padding: 0 }
            }
        });
    }

    // 第二页：语言分布 (ECharts 紧凑版)
    function createLanguageChart() {
        const languageData = analysisData.most_used_language || [];
        const chartDiv = document.getElementById('languageChart');
        
        // 取 Top 5 语言，防止条目太多撑不开
        const sortedLangs = languageData.sort((a,b) => b.counts - a.counts).slice(0, 5);
        
        const languages = {};
        sortedLangs.forEach(item => {
            languages[item.language] = parseInt(item.counts || 0);
        });

        const option = {
            // 【关键】极小的边距，利用每一寸空间
            grid: { top: 5, right: 10, bottom: 5, left: 5, containLabel: true },
            xAxis: { type: 'value', show: false },
            yAxis: { 
                type: 'category', 
                data: Object.keys(languages),
                axisLine: { show: false },
                axisTick: { show: false },
                axisLabel: { 
                    fontSize: 10,
                    width: 70, // 限制文字宽度
                    overflow: 'truncate' 
                }
            },
            series: [{
                data: Object.values(languages),
                type: 'bar',
                barWidth: 12, // 细条
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                        { offset: 0, color: '#667eea' },
                        { offset: 1, color: '#764ba2' }
                    ]),
                    borderRadius: [0, 6, 6, 0]
                },
                label: {
                    show: true,
                    position: 'right',
                    fontSize: 9,
                    formatter: '{c}'
                }
            }]
        };

        if (charts.language) charts.language.dispose();
        charts.language = echarts.init(chartDiv);
        charts.language.setOption(option);
    }

    // 第三页：小时分布 (紧凑版)
    // 第三页：小时分布 (修复：颜色改成深色，防止在白底上看不见)
// 第三页：小时分布 (已开启纵轴显示)
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

        // 紫色渐变
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, '#667eea');
        gradient.addColorStop(1, '#764ba2');

        charts.hourly = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: fullHours, 
                datasets: [{
                    label: '对话次数',
                    data: fullValues,
                    backgroundColor: gradient,
                    borderRadius: 4,
                    barPercentage: 0.6,
                    hoverBackgroundColor: '#764ba2'
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
                        bodyColor: '#fff'
                    }
                },
                scales: {
                    x: { 
                        grid: { display: false }, 
                        ticks: { 
                            color: '#888',
                            font: { size: 9 },
                            maxRotation: 0,
                            autoSkip: true,
                            maxTicksLimit: 8
                        } 
                    },
                    // 【修改部分】开启 Y 轴
                    y: { 
                        display: true, // 1. 改为 true 显示
                        beginAtZero: true,
                        border: { display: false }, // 2. 隐藏左侧竖线，更美观
                        grid: { 
                            color: '#f0f0f0', // 3. 设置淡淡的网格线
                            drawBorder: false 
                        },
                        ticks: { 
                            color: '#888', // 文字颜色
                            font: { size: 9 }, // 字号小一点
                            maxTicksLimit: 5 // 4. 限制刻度数量，防止太密
                        }
                    } 
                },
                layout: { padding: 0 },
                animation: {
                    duration: 1500,
                    easing: 'easeOutQuart'
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

    // ==========================================
    // 修改函数 2: generateCharactersCopy
    // ==========================================
    function generateCharactersCopy() {
        // 重新计算总数用于文案对比
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

        const box = document.getElementById('charactersCopy');
        
        // 计算倍率 (AI 写了多少字 / 用户写了多少字)
        const ratio = userTotal > 0 ? (aiTotal / userTotal).toFixed(1) : 0;

        // 依然保留之前的哈利波特/电影对比，因为总产出依然很壮观
        const hpWords = 1100000; 
        const novels = (grandTotal / hpWords).toFixed(2);
        
        const templates = [
            `这一年，你每敲下 1 个字，AI 就会回馈给你 ${ratio} 个字的灵感。`,
            `你们一共创造了 ${formatNumber(grandTotal)} 字符，相当于合写了 ${novels} 本《哈利波特》。`,
            `你的 ${formatNumber(userTotal)} 字提问，撬动了 AI ${formatNumber(aiTotal)} 字的庞大思考。`
        ];
        
        box.textContent = pickOne(templates);
    }

    function generateMonthCopy() {
        const chatDaysData = analysisData.chat_days || [];
        if (!chatDaysData.length) return;
        
        const monthCounts = {};
        chatDaysData.forEach(({ date, counts }) => {
            const m = new Date(date).getMonth() + 1;
            monthCounts[m] = (monthCounts[m] || 0) + parseInt(counts || 0);
        });
        
        // 找到最活跃的月份
        const topMonth = Object.keys(monthCounts).sort((a, b) => monthCounts[b] - monthCounts[a])[0];
        
        const templates = {
            1: ['新年伊始，和 AI 的互动就已拉满！', '一月的新计划，AI 是你的贴身参谋。'],
            2: ['二月虽短，但你和 AI 的灵感很长。', '开春之际，学习热情率先点燃。'],
            3: ['三月万物复苏，你的思维也在疯狂生长。', '不仅春暖花开，你的效率也在发芽。'],
            4: ['四月人间天，你和 AI 的配合似神仙。', '论文与方案，AI 是你最温柔的辅助。'],
            5: ['五月有劳动节，你确实在与 AI 辛勤协作。', '假期可以休，但求知欲从不打烊。'],
            6: ['六月期末冲刺，AI 陪你一起打怪升级。', '把“DDL”打成“Done”，这波配合满分。'],
            7: ['七月流火，你的思考热度也不减半分。', '盛夏除了空调，AI 是你最好的冷静剂。'],
            8: ['八月积蓄力量，AI 充实了你的技能库。', '为了下半年的爆发，你在这个月默默耕耘。'],
            9: ['九月新起点，AI 是你的全能导航员。', '金秋收获季，知识也在这一刻结果。'],
            10: ['十月长假归来，新灵感和 AI 一起落地。', '国庆之后，你和 AI 的默契更上一层楼。'],
            11: ['十一月不只购物，还在给大脑疯狂“进货”。', '年末前的冲刺，每一步都算数。'],
            12: ['十二月完美收官，AI 见证了你一年的成长。', '年终复盘，AI 是你最忠实的记录者。']
        };
        const text = pickOne(templates[topMonth] || ['这一年，你和 AI 的默契刚刚好。']);
        document.getElementById('monthCopy').innerHTML = `<span style="color:#667eea;font-size:1.2em">${topMonth}月</span> <br> ${text}`;
    }


    function generateSessionsCopy() {
        const count = analysisData.session_count?.session_count || 0;
        let templates = [];
        if (count > 300) {
            templates = ['近乎“日更”的高频交流，AI 已经是你的生活必需品。', '比点外卖还勤快，这一年你真的很努力。'];
        } else if (count > 100) {
            templates = ['每一次对话都是一次灵感捕捉，你做到了上百次。', '频繁却不盲目，你掌握了驾驭 AI 的最佳节奏。'];
        } else {
            templates = ['不常闲聊，但次次切中要害。', '你把 AI 当作精确的工具，用在了刀刃上。'];
        }
        document.getElementById('sessionsCopy').textContent = pickOne(templates);
    }

    // 第二页内容
    function generateModelsCopy() {
        const models = analysisData.most_used_models || [];
        const topModel = models.length > 0 ? models[0].model : '';
        const box = document.getElementById('modelsCopy');
        
        let text = '';
        if (topModel.includes('reasoner')) {
            text = '你偏爱深思熟虑，<br><b>Reasoner</b> 的逻辑链与你产生共鸣。';
        } else if (topModel.includes('chat') || topModel.includes('gpt')) {
            text = '你喜欢高效直接，<br><b>Chat</b> 模式是你解决问题的快刀。';
        } else {
            text = '你的工具箱很丰富，<br>每一种模型都在关键时刻出手。';
        }
        box.innerHTML = text;
    }

    function generateLanguageCopy() {
        const data = analysisData.most_used_language || [];
        const box = document.getElementById('languageCopy');
        let lines = [];
        
        // 简易判断
        const hasPython = data.some(d => d.language.toLowerCase().includes('python'));
        const hasCpp = data.some(d => d.language.toLowerCase().includes('cpp') || d.language.toLowerCase().includes('c++'));
        const hasEnglish = data.some(d => d.language.toLowerCase().includes('english'));

        if (hasPython) lines.push('🐍 Python 让灵感自动化，你的代码很有灵性。');
        if (hasCpp) lines.push('⚡ C++ 展现了硬核一面，追求极致性能。');
        if (hasEnglish) lines.push('🌍 英语交流无障碍，你的知识边界在世界范围延伸。');
        if (lines.length === 0) lines.push('📝 中文逻辑严密，你把复杂问题阐述得清清楚楚。');
        
        box.innerHTML = lines.slice(0, 2).map(l => `<div>${l}</div>`).join('');
    }

    // 第三页内容
    function generateHourlyCopy() {
        const hourly = analysisData.per_hour_distribution || {};
        const maxHour = Object.keys(hourly).reduce((a, b) => hourly[b] > (hourly[a] || 0) ? b : a, '12');
        const h = parseInt(maxHour);
        
        let text = '';
        if (h >= 0 && h < 6) text = '深夜依旧清醒，星星和 AI 见过你最努力的样子。';
        else if (h < 12) text = '一日之计在于晨，清晨是你灵感爆发的高光时刻。';
        else if (h < 18) text = '午后时光，你和 AI 的配合稳中有进，效率拉满。';
        else text = '夜幕降临，思维反而更加活跃，这是属于你的沉浸时刻。';
        
        document.getElementById('hourlyCopy').textContent = text;
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

    function generateTimeCopy() {
        const box = document.getElementById('timeCopy');
        box.textContent = '时间记录着思考的轨迹，每一分钟都没有被辜负。';
    }

    // 第四页内容
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
        
        const box = document.getElementById('politenessSummary');
        const total = pCount + iCount;
        const ratio = total ? (pCount / total) : 1;
        
        let text = '';
        if (ratio > 0.8) text = '礼貌指数爆表！你把 AI 当作值得尊重的伙伴，AI 也一定很喜欢为你服务。';
        else if (ratio > 0.5) text = '直率又真实，你与 AI 的交流高效且不拘小节。';
        else text = '有点“刚”哦，不过 AI 理解你的急切，下次试试多点温柔？';
        
        box.textContent = text;
    }

    function generateRefuseCopy() {
        const count = analysisData.refuse_counts || 0;
        document.getElementById('refuseCount').textContent = count;
        
        const box = document.getElementById('refuseCopy');
        let text = '';
        if (count > 50) text = '你试图跟 AI 聊些“不能说的秘密”，嘿嘿，它守口如瓶。';
        else if (count > 10) text = '偶尔触碰边界，这是你探索欲的体现。';
        else if (count === 0) text = '100% 回复率！看来 AI 从未对你“冷暴力”。';
        else text = '沟通顺畅，大多数时候你们都在同一个频道上。';
        
        box.textContent = text;
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
    // 8. 导出功能 (核心修改)
    // ==========================================

    // ==========================================
    // 8. 导出功能 (核心修改：修复背景模糊问题)
    // ==========================================
// ==========================================
    // 8. 导出功能 (终极修正版：合成法)
    // ==========================================
    
    async function exportPagesAsImages() {
        if (!window.html2canvas) {
            alert('导出模块加载中，请稍后再试...');
            return;
        }

        const navArrows = document.querySelector('.nav-arrows');
        const actionArea = document.querySelector('.action-area');
        
        // 1. 隐藏干扰元素
        if (navArrows) navArrows.style.display = 'none';
        if (actionArea) actionArea.style.visibility = 'hidden';

        const exportPageIndices = [1, 2, 3, 4];
        
        try {
            for (let i of exportPageIndices) {
                // 切换到该页
                showPage(i);
                
                // 等待图表和DOM稳定
                await new Promise(resolve => setTimeout(resolve, 600));

                // 获取当前页面的卡片容器
                const currentPageEl = document.getElementById(`page${i}`);
                const cardEl = currentPageEl.querySelector('.card-container');

                if (!cardEl) continue;

                // --- 核心修改：手动合成背景和卡片 ---

                // 1. 捕捉卡片 (强制白底，确保清晰)
                // 临时设置卡片样式以保证截图清晰
                const originalBg = cardEl.style.background;
                const originalShadow = cardEl.style.boxShadow;
                cardEl.style.background = '#ffffff'; // 强制纯白
                cardEl.style.boxShadow = 'none';     // 暂时移除阴影，稍后画上去或忽略

                // 截取卡片
                const cardCanvas = await html2canvas(cardEl, {
                    scale: 2,
                    useCORS: true,
                    backgroundColor: '#ffffff' // 确保卡片背景不透明
                });

                // 恢复卡片原样
                cardEl.style.background = originalBg;
                cardEl.style.boxShadow = originalShadow;

                // 2. 创建最终画布 (模拟手机屏幕尺寸)
                const finalCanvas = document.createElement('canvas');
                const width = 1080;  // 设定高分辨率宽
                const height = 1920; // 设定高分辨率高
                finalCanvas.width = width;
                finalCanvas.height = height;
                const ctx = finalCanvas.getContext('2d');

                // 3. 绘制渐变背景 (直接画在 canvas 上，不依赖 DOM 截图)
                // 获取当前 body 的背景样式，或者直接使用预设的漂亮渐变
                // 这里我们手动创建一个对应当前时间的完美渐变
                const gradient = ctx.createLinearGradient(0, 0, width, height);
                // 默认使用清新蓝绿渐变 (Day Theme)，你也可以根据 body 类名判断
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
                    // Default / Day
                    gradient.addColorStop(0, '#84fab0');
                    gradient.addColorStop(1, '#8fd3f4');
                }
                
                ctx.fillStyle = gradient;
                ctx.fillRect(0, 0, width, height);

                // 4. 将截好的卡片画到正中间
                // 计算卡片在画布中的尺寸（保持比例）
                const cardAspect = cardCanvas.width / cardCanvas.height;
                const drawWidth = width * 0.85; // 卡片占宽度的 85%
                const drawHeight = drawWidth / cardAspect;
                const drawX = (width - drawWidth) / 2;
                const drawY = (height - drawHeight) / 2;

                // 4.1 (可选) 手动画一个简单的阴影
                ctx.save();
                ctx.shadowColor = "rgba(0, 0, 0, 0.2)";
                ctx.shadowBlur = 40;
                ctx.shadowOffsetY = 20;
                // 绘制卡片
                ctx.drawImage(cardCanvas, drawX, drawY, drawWidth, drawHeight);
                ctx.restore();

                // 5. 导出
                const link = document.createElement('a');
                link.download = `AI_Memory_2024_Page_${i}.png`;
                link.href = finalCanvas.toDataURL('image/png');
                link.click();
            }
        } catch (err) {
            console.error('导出失败:', err);
            alert('导出遇到问题，请重试');
        } finally {
            if (navArrows) navArrows.style.display = 'flex';
            if (actionArea) actionArea.style.visibility = 'visible';
            
            setTimeout(() => {
                 alert('✅ 导出完成！画面已修复清晰。');
            }, 500);
        }
    }
});