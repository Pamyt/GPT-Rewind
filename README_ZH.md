# GPT-Rewind
一个简单的 AI 年度总结工具

中文版 | [English](README.md)

<img src="assets/imgs/icon.svg" width="150" alt="GPTLens Logo" />

一个全面的 AI 对话历史分析工具，提供与 AI 模型交互模式的洞察和可视化。

## 功能特点

- **年度总结**：通过详细统计信息获取您的 AI 聊天历史完整概览
- **可视化分析**：显示使用模式、时间分布和语言偏好的交互式图表
- **多模型支持**：分析不同 AI 模型的对话
- **语言检测**：识别使用的自然语言和编程语言
- **行为洞察**：揭示礼貌模式、表情符号使用和交互风格
- **导出功能**：将您的年度总结保存为图片

## 更新日志
- 2025/12/19 支持 Claude 模型 🎉
- 2025/12/19 支持 Qwen 模型 🎉
- 2025/12/13 支持 Windows 平台 🎉 感谢 [@zengly22](https://github.com/zengly22) 的错误报告

## 安装

### 运行条件

- Python 3.7 或更高版本
- pip 包管理器

### 开始前

1. 克隆此仓库：
```bash
git clone https://github.com/yourusername/GPT-Rewind.git
cd GPT-Rewind
```

2. 运行脚本：
- 在 macOS/Linux 上：
```bash
bash ./start_frontend.sh
```
- 在 Windows 上：
```bash
.\start_frontend.bat
```

3. 打开浏览器并访问 `http://localhost:5173`

## 使用方法

### DeepSeek 用户

1. **从 DeepSeek 网站下载您的聊天历史**：
   - 前往您的 DeepSeek 账户设置
   - 找到数据导出选项
   - 将您的对话历史下载为 JSON 文件

![下载聊天历史](assets/usage/deepseek.png)

2. **上传聊天历史**：
   - 点击"上传 JSON 记录"按钮
   - 选择 AI 平台
   - 选择您下载的 JSON 文件
   - 等待分析完成

3. **开始探索**：
   - 使用方向键或屏幕按钮导航不同页面
   - 查看年度概览、AI 伙伴、时间模式和交互风格
   - 使用"保存年度记忆"按钮将总结导出为图片

### Qwen 用户

1. **从 Qwen 网站下载您的聊天历史**：
   - 前往您的 Qwen 账户设置
   - 找到数据导出选项
   - 将您的对话历史下载为 JSON 文件

![下载聊天历史](assets/usage/qwen.png)

2. **上传聊天历史**：
   - 点击"上传 JSON 记录"按钮
   - 选择 AI 平台
   - 选择您下载的 JSON 文件
   - 等待分析完成

3. **开始探索**：
   - 使用方向键或屏幕按钮导航不同页面
   - 查看年度概览、AI 伙伴、时间模式和交互风格
   - 使用"保存年度记忆"按钮将总结导出为图片

### Claude 用户

1. **从 Claude 网站下载您的聊天历史**：
   - 前往您的 Claude 账户设置
   - 找到数据导出选项
   - 将您的对话历史下载为 JSON 文件

![下载聊天历史](assets/usage/claude.png)

2. **上传聊天历史**：
   - 点击"上传 JSON 记录"按钮
   - 选择 AI 平台
   - 选择您下载的 JSON 文件
   - 等待分析完成

3. **开始探索**：
   - 使用方向键或屏幕按钮导航不同页面
   - 查看年度概览、AI 伙伴、时间模式和交互风格
   - 使用"保存年度记忆"按钮将总结导出为图片

## API 端点

应用程序提供以下 REST API 端点：

- `GET /` - 主 Web 界面
- `POST /api/upload` - 上传聊天历史 JSON 文件
- `POST /api/analyze` - 分析上传的聊天数据
- `GET /health` - 健康检查端点

## 项目结构

```
GPT-Rewind/
├── rewind/                 # 核心分析模块
│   ├── apis/              # 数据分析的 API 端点
│   ├── data_process/      # 数据处理工具
│   └── utils/             # 辅助函数
├── frontend/              # Web 界面
│   ├── static/           # CSS 和 JavaScript 文件
│   └── templates/        # HTML 模板
├── data/                 # 示例数据
├── assets/               # 图片和资源
└── tests/               # 测试文件
```

## 依赖项

主要依赖项包括：
- Flask: Web 框架
- pandas: 数据处理
- plotly: 数据可视化
- numpy: 数值计算
- requests: HTTP 客户端

完整列表请参见 [`requirements.txt`](requirements.txt)。

## 贡献

1. Fork 此仓库
2. 创建功能分支
3. 进行更改
4. 如适用，添加测试
5. 提交拉取请求

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

## 支持

如果遇到任何问题：
1. 检查 JSON 文件是否符合预期格式
2. 确保所有依赖项已正确安装
3. 检查服务器日志中的错误消息
4. 在 GitHub 上创建 Issue，详细说明您的问题
