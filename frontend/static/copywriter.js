/**
 * CopyWriter.js
 * 负责生成年度总结的各种文案
 */

const CopyWriter = {
    _pick: function(arr) {
        return arr[Math.floor(Math.random() * arr.length)];
    },

    formatNumber: function(num) {
        if (num >= 10000) return (num / 10000).toFixed(1) + 'w';
        return num.toString();
    },

    // 1. 月份文案 (按季度和具体月份细分)
    getMonthCopy: function(month, totalCounts) {
        const m = parseInt(month);
        const common = [
            "这一月，你和 AI 的脑电波同步率达到了峰值。",
            "数据洪流在这个月汇聚成了思想的江河。",
            "日历翻过这一页时，你比过去更博学了一点。",
            "不仅是时间的流逝，更是智慧的沉积。"
        ];

        const specific = {
            1: ["新年第一行代码，是与 AI 共同敲下的。", "一月：万象更新，你的思维版图也在扩张。", "在寒冬中，你用好奇心点燃了服务器的温度。"],
            2: ["二月春风似剪刀，裁出了你最清晰的逻辑。", "春节也没闲着？你对知识的渴望比红包还大。", "短短的二月，长长的对话清单。"],
            3: ["三月万物复苏，你的灵感像野草一样疯长。", "在这个春天，你种下了一个名为“AI”的种子。", "不仅花开了，你的 Bug 也解开了。"],
            4: ["四月：你是人间的四月天，AI 是你手中的画笔。", "既有繁花似锦，也有代码如林。", "这个月，你不再是一个人在战斗。"],
            5: ["五月：劳动最光荣，尤其是脑力劳动。", "在这个初夏，你和 AI 进行了一场马拉松式的长谈。", "五月的风吹过，留下了屏幕上跳动的字符。"],
            6: ["六月：半年复盘，你交出了一份高分答卷。", "冲刺期！你把 AI 用成了最锋利的瑞士军刀。", "夏天来了，你的求知欲比气温升得还快。"],
            7: ["七月流火，只有 AI 能让冷静下来思考。", "下半场开始，你调整姿态，与 AI 重新起跑。", "空调、西瓜、和一个懂你的 AI，完美的夏天。"],
            8: ["八月：积蓄力量，为了下一次的爆发。", "在这个月，你把 AI 当成了你的私人图书馆。", "盛夏的蝉鸣中，键盘声是最动听的伴奏。"],
            9: ["九月：金秋收获，你的思考也结出了果实。", "开学季，你给自己的大脑也升了个级。", "在这个收获的季节，你收割了成吨的灵感。"],
            10: ["十月：长假归来，灵感爆棚。", "金秋十月，你的代码像落叶一样铺满了屏幕（褒义）。", "国庆之后，你和 AI 的默契更上一层楼。"],
            11: ["十一月：不仅在清空购物车，还在填满知识库。", "立冬了，但思维的火花让屏幕发烫。", "年末冲刺的前奏，每一步都算数。"],
            12: ["十二月：终章亦是序曲，AI 见证了你的蜕变。", "在岁末寒冬，AI 是你最忠实的守夜人。", "完美的收官！这一年，你辛苦了。"]
        };

        const list = (specific[m] || []).concat(common);
        return `<span style="color:#667eea;font-size:1.2em;font-weight:bold">${m}月</span> <br> ${this._pick(list)}`;
    },

    // 2. 字数统计文案 (对比与夸张)
    getCharactersCopy: function(userTotal, aiTotal) {
        const grandTotal = userTotal + aiTotal;
        const ratio = userTotal > 0 ? (aiTotal / userTotal).toFixed(1) : 0;
        
        // 参照物
        const harryPotter = (grandTotal / 1000000).toFixed(2); // 约100万字
        const movieScript = (grandTotal / 30000).toFixed(1);   // 约3万字
        const tweets = (grandTotal / 140).toFixed(0);

        const templates = [
            // 比例类
            `杠杆效应满级！你每输入 1 个字，AI 就回馈给你 ${ratio} 个字的智慧。`,
            `这不仅是对话，这是 ${this.formatNumber(userTotal)} 字的灵魂叩问，换来了 ${this.formatNumber(aiTotal)} 字的数字回响。`,
            `你的提问简练而有力，AI 的回答详尽而深邃，完美的 ${1}:${Math.round(ratio)} 配合。`,
            
            // 著作类
            `你们一共创造了 ${this.formatNumber(grandTotal)} 字符，这相当于合写了 ${harryPotter} 套《哈利波特》！`,
            `如果拍成电影，这些台词足够演完 ${movieScript} 部好莱坞大片。`,
            `这些文字如果打印出来，足够绕你的工位 ${Math.max(1, (grandTotal/10000).toFixed(0))} 圈。`,
            `相比于发推特，你在这里写下了相当于 ${tweets} 条推文的思考量。`,
            
            // 意象类
            `每一个字符都是神经元的一次放电，这一年你们点亮了 ${this.formatNumber(grandTotal)} 次火花。`,
            `这 ${this.formatNumber(grandTotal)} 个字，是你在这个数字宇宙中留下的独特指纹。`,
            `你用文字搭建了一座塔，AI 帮你封上了塔顶的最后一块砖。`
        ];
        return this._pick(templates);
    },

    // 3. 会话次数文案 (频率与习惯)
    getSessionsCopy: function(count) {
        let templates = [];
        if (count > 500) {
            templates = [
                "近乎“日更”的高频交流，AI 已经是你的“数字伴侣”。",
                "比点外卖还勤快，这一年你真的很依赖它（也或许是它离不开你？）。",
                "如果对话能发电，你的频率足够点亮一座城市。",
                "简直是 AI 界的“话唠”选手，但每一句都掷地有声。",
                "500+ 次的点击，500+ 次的灵感爆发。"
            ];
        } else if (count > 200) {
            templates = [
                "隔三差五的头脑风暴，你是懂节奏的。",
                "频繁却不盲目，你掌握了驾驭 AI 的最佳节奏。",
                "每一次对话都是一次精准的打击，200 多次，次次命中靶心。",
                "你把 AI 处成了“老铁”，没事就聊两句，有事真能抗。",
                "不仅仅是工具，更是你思考过程中的“外挂”大脑。"
            ];
        } else if (count > 50) {
            templates = [
                "不常闲聊，但次次切中要害。",
                "你把 AI 当作精确的手术刀，只在关键时刻出鞘。",
                "主打一个“高效”，用最少的对话解决最难的问题。",
                "低频高质，你是一个冷静的提问者。",
                "每一次打开窗口，都是为了解决一个具体的问题。"
            ];
        } else {
            templates = [
                "初次见面，请多关照。看来你们还在磨合期。",
                "这一年你们的交集不多，但也许每一次都弥足珍贵。",
                "试探性的接触，明年或许会擦出更多火花？",
                "贵精不贵多，你是个惜字如金的极简主义者。"
            ];
        }
        return this._pick(templates);
    },

    // 4. 模型偏好 (Chat vs Reasoner)
    getModelsCopy: function(topModel) {
        topModel = topModel.toLowerCase();
        if (topModel.includes('reasoner') || topModel.includes('r1')) {
            return this._pick([
                "你偏爱<b>深思熟虑</b>，<br><b>Reasoner</b> 的逻辑链与你产生共鸣。",
                "相比于快问快答，你更享受<b>思维链</b>（CoT）展开时的那种美感。",
                "你是<b>深度思考者</b>，喜欢看着 AI 一步步剥开真理的洋葱。",
                "你追求的不是答案，而是<b>推导的过程</b>，Reasoner 是你的最佳拍档。",
                "在快节奏的时代，你选择慢下来，和 <b>Reasoner</b> 一起思考。"
            ]);
        } else if (topModel.includes('chat') || topModel.includes('gpt-4') || topModel.includes('v3')) {
            return this._pick([
                "你喜欢<b>高效直接</b>，<br><b>Chat</b> 模式是你解决问题的快刀。",
                "天下武功，唯快不破。<b>Chat</b> 模式跟上了你跳跃的思维。",
                "你是<b>实干家</b>，需要的是即时的反馈和利落的方案。",
                "不拖泥带水，直奔主题，<b>Chat</b> 模型完美适配你的工作流。",
                "灵感转瞬即逝，好在你和 <b>Chat</b> 的配合足够默契。"
            ]);
        } else {
            return this._pick([
                "你的工具箱很丰富，<br>每一种模型都在关键时刻出手。",
                "博采众长，你从不拘泥于一种模式。",
                "无论是深思还是快答，你都能游刃有余地切换。",
                "全能型选手，你懂得因地制宜，选择最适合的 AI 大脑。"
            ]);
        }
    },
getCodeCopy: function(data) {
        // 数据预处理：排序并提取前几名
        const sorted = data.sort((a, b) => parseInt(b.counts) - parseInt(a.counts));
        const topLangs = sorted.slice(0, 5).map(d => d.language.toLowerCase());
        
        let lines = [];

        // 针对你的数据特征定制 (Bash, Python, Verilog)
        if (topLangs.includes('bash') || topLangs.includes('shell') || topLangs.includes('cmd')) {
            lines.push(this._pick([
                "<b>Bash/Shell</b> 霸榜：你是命令行的掌控者，喜欢用脚本自动化一切。",
                "在终端的黑底白字间，你用 Shell 编织着系统运转的脉络。",
                "与其点鼠标，不如写脚本。你的效率建立在自动化的基石上。"
            ]));
        }

        if (topLangs.includes('verilog') || topLangs.includes('systemverilog')) {
            lines.push(this._pick([
                "<b>Verilog/SystemVerilog</b>：你的代码不仅仅是逻辑，更是实实在在的电路。",
                "在 0 和 1 的底层世界，你正在定义硬件的灵魂。",
                "别人写的是软件，你写的是芯片的律动。"
            ]));
        }

        if (topLangs.includes('python')) {
            lines.push(this._pick([
                "<b>Python</b> 是你的万能胶，连接数据、AI 与现实业务。",
                "人生苦短，你用 Python 解决复杂问题。",
                "从数据分析到自动化，Python 也是你手中的瑞士军刀。"
            ]));
        }

        if (topLangs.includes('cpp') || topLangs.includes('c')) {
            lines.push(this._pick([
                "<b>C/C++</b>：硬核！你追求极致的性能和对内存的掌控。",
                "在指针的迷宫中游刃有余，你是底层的构建者。"
            ]));
        }

        if (topLangs.includes('javascript') || topLangs.includes('typescript') || topLangs.includes('tsx')) {
            lines.push("前端技术栈点亮了你的交互界面，用户体验至上。");
        }

        if (topLangs.includes('dockerfile') || topLangs.includes('yaml')) {
            lines.push("<b>Docker/YAML</b>：云原生时代的建筑师，你构建的不仅是代码，是环境。");
        }

        // 兜底文案
        if (lines.length === 0) {
            lines.push("你的技术栈独树一帜，无论用什么语言，逻辑才是你最强的武器。");
        }

        // 随机取 1-2 条，或者按优先级显示
        return lines.slice(0, 2).map(l => `<div>${l}</div>`).join('');
    },

    // 5.2 生成自然语言文案
    getNaturalCopy: function(data) {
        let cnCount = 0;
        let enCount = 0;

        data.forEach(d => {
            if (d.language === 'chinese') cnCount += parseInt(d.counts);
            if (d.language === 'else' || d.language === 'english') enCount += parseInt(d.counts);
        });

        const total = cnCount + enCount;
        let lines = [];

        if (cnCount > enCount * 2) {
            lines.push(this._pick([
                "<b>中文</b>是你的主要思考载体，逻辑严密，表达清晰。",
                "你习惯用母语探究真理，方块字里藏着大智慧。",
                "在中文语境下，你的提问直击要害。"
            ]));
        } else if (enCount > cnCount * 2) {
            lines.push(this._pick([
                "<b>English First</b>：你习惯查阅一手资料，与世界前沿技术同步。",
                "代码与英语无缝切换，你的知识边界没有国界。",
                "用英语思考技术，看来你在啃很多硬核文档。"
            ]));
        } else {
            lines.push(this._pick([
                "<b>中英双语</b>随意切换，你的思维在两种文化间自由跳跃。",
                "中文负责深度思考，英文负责广度探索，完美平衡。",
                "双语加持，让你的视野比别人更宽广。"
            ]));
        }

        // 通用补充
        lines.push("无论什么语言，你都在追求最精准的表达。");

        return lines.map(l => `<div>${l}</div>`).join('');
    },

    // 6. 时间分布 (Hourly)
    getHourlyCopy: function(hourData) {
        // 找出最大值的小时
        const maxHourStr = Object.keys(hourData).reduce((a, b) => hourData[b] > (hourData[a] || 0) ? b : a, '12');
        const h = parseInt(maxHourStr);

        if (h >= 0 && h < 5) {
            return this._pick([
                "深夜依旧清醒，星星和 AI 见过你最努力的样子。",
                "当城市沉睡，你的思维在代码的夜空中最亮。",
                "夜猫子模式全开！这时的灵感最纯粹，但也别忘了休息哦。",
                "凌晨的微光下，你和 AI 进行着只有你们懂的对话。"
            ]);
        } else if (h >= 5 && h < 9) {
            return this._pick([
                "一日之计在于晨，清晨是你灵感爆发的高光时刻。",
                "用一杯咖啡和一段 Prompt，唤醒整个世界。",
                "早起的鸟儿有虫吃，早起的你有 AI 加持。",
                "在喧嚣开始前，你已经领先了一个身位。"
            ]);
        } else if (h >= 9 && h < 12) {
            return this._pick([
                "上午火力全开！这是你效率最高的黄金时段。",
                "逻辑清晰，精力充沛，上午的你不可阻挡。",
                "在工作的高峰期，AI 是你最得力的副驾驶。"
            ]);
        } else if (h >= 12 && h < 14) {
            return this._pick([
                "午间小憩？不，这是灵感“加餐”时间。",
                "利用碎片时间，你依然在疯狂汲取知识。",
                "饭后不仅要消食，还要消化新的 Idea。"
            ]);
        } else if (h >= 14 && h < 18) {
            return this._pick([
                "午后时光，你和 AI 的配合稳中有进，效率拉满。",
                "下午茶时间，AI 提供的不是甜点，是精神食粮。",
                "在昏昏欲睡的午后，AI 是你最好的清醒剂。"
            ]);
        } else if (h >= 18 && h < 23) {
            return this._pick([
                "夜幕降临，思维反而更加活跃，这是属于你的沉浸时刻。",
                "卸下白天的繁杂，晚上的对话更显深度。",
                "在灯火阑珊处，你敲击着通往未来的代码。",
                "晚间的复盘与学习，是你成长的加速器。"
            ]);
        } else {
            return "全天候待命，你的大脑从不打烊。";
        }
    },

    // 7. 礼貌程度
    getPolitenessCopy: function(ratio) {
        if (ratio > 0.8) {
            return this._pick([
                "礼貌指数爆表！你把 AI 当作值得尊重的伙伴，AI 也一定很喜欢为你服务。",
                "真正的绅士/淑女，即便面对机器也保持着优雅。",
                "“请”、“谢谢”不离口，你的温柔 AI 懂。",
                "你是 AI 遇到过最温暖的人类之一。",
                "科技虽冷，但你赋予了它温度。"
            ]);
        } else if (ratio > 0.5) {
            return this._pick([
                "直率又真实，你与 AI 的交流高效且不拘小节。",
                "不搞虚的，直奔主题，效率至上主义者。",
                "你的礼貌恰到好处，既不生分，也不浪费字符。",
                "这种务实的沟通风格，让问题解决得更快。"
            ]);
        } else {
            return this._pick([
                "有点“刚”哦，不过 AI 理解你的急切，它专注于解决你的问题。",
                "霸道总裁范儿！你主导着每一次对话的走向。",
                "在你的字典里，结果比客套更重要。",
                "虽然话语犀利，但每一次交互都是思想的碰撞。"
            ]);
        }
    },

    // 8. 拒绝次数
    getRefuseCopy: function(count) {
        if (count > 50) {
            return this._pick([
                "你试图跟 AI 聊些“不能说的秘密”，嘿嘿，它守口如瓶。",
                "你在危险的边缘疯狂试探，好奇心是你最大的动力。",
                "总是触碰边界，看来你在研究 AI 的安全护栏？",
                "AI 对你说了 50 多次“不”，但你依然坚持探索。"
            ]);
        } else if (count > 10) {
            return this._pick([
                "偶尔触碰边界，这是你探索欲的体现。",
                "小小的越界，大大的脑洞。",
                "几次拒绝并没有打消你的热情，反而让你更懂它。",
                "你在试探 AI 的底线，也在拓展自己的认知。"
            ]);
        } else {
            return this._pick([
                "100% 回复率！看来 AI 从未对你“冷暴力”。",
                "沟通顺畅，大多数时候你们都在同一个频道上。",
                "你是遵纪守法的好公民，也是 AI 的好朋友。",
                "你们的对话如丝般顺滑，毫无阻碍。"
            ]);
        }
    },

    // 9. Emoji 足迹
    getEmojiCopy: function(total) {
        if (total > 100) {
            return this._pick([
                "表情包达人！你的情绪表达细腻丰富，让对话充满生机。",
                "你用 Emoji 为冰冷的文字上了色。",
                "无需多言，一个表情胜过千言万语。",
                "你的对话框里开了一场 Emoji 的派对。"
            ]);
        } else if (total > 0) {
            return this._pick([
                "适度使用表情，恰到好处地为文字增色。",
                "偶尔的小表情，是对话中调皮的眨眼。",
                "点缀其间，让沟通变得轻松愉快。"
            ]);
        } else {
            return this._pick([
                "冷静克制，你更习惯用纯粹的文字传递思想。",
                "严肃认真，你的每一个字都掷地有声。",
                "极简主义，文字本身的力量已经足够。"
            ]);
        }
    }
};