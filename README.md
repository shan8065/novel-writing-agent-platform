# 小说创作智能体平台

一个基于Trae Skill系统的模块化小说创作智能体平台，专为网文作者设计。

## 项目特点

- **13个专门化智能体**：从资料整理到质量审核的完整创作流水线
- **三种工作模式**：全新小说创作、续写已有小说、混合创作（SCP+崩坏3）
- **多源素材整合**：支持SCP基金会文档、崩坏3角色等素材的深度整合
- **质量保证**：内置连贯性检查智能体，确保人物性格和情节逻辑一致

## 智能体列表

### 资料处理类
- `deepseek-html-processor` - 从DeepSeek保存的TXT文件中提取创作资料
- `scp-extractor` - 从SCP PDF文档中提取纯文本内容
- `scp-archiver` - 管理和归档多个SCP文档，建立知识库索引
- `storyline-organizer` - 整理完整故事线，帮助了解故事全貌

### 角色与设定类
- `honkai-character-integrator` - 处理崩坏3角色PDF并融入故事世界观
- `character-scp-integrator` - 将角色设定与SCP文档能力细节相结合
- `lore-organizer` - 整理和管理小说设定资料（角色档案、世界观、时间线等）
- `setting-reader` - 阅读并整理所有设定资料，确保创作符合设定

### 创作类
- `story-writer` - 专门负责撰写小说内容，创作章节、段落和对话
- `novel-continuer` - 继续已有小说的创作，保持故事连贯性

### 质量控制类
- `coherence-checker` - 监督故事连贯性，检查人物性格、情节逻辑、时间线等

### 工具类
- `html-to-pdf-converter` - 将HTML文件1:1精确转换为PDF格式

## 技术栈

- **Trae Skill系统** - 智能体框架
- **Python** - 后端脚本开发
- **Playwright** - HTML转PDF转换
- **大模型API** - 智能创作核心

## 项目结构

```
e:\小说/
├── .trae/skills/          # Trae技能文件
├── SCP/                    # SCP HTML文档
├── SCP_PDF/                # SCP PDF文档
├── 崩坏3角色/              # 崩坏3角色资料
├── 角色/                   # 原创角色设定
├── 与deepseek一起创作小说章节/  # 已创作的小说章节
├── convert_html_to_pdf.py  # HTML转PDF转换脚本
└── skill使用教程.txt       # 完整的使用教程
```

## 使用示例

### 全新SCP+崩坏3小说创作
1. 调用 `novel-master-orchestrator` 主控智能体
2. 自动调度：资料提取 → 设定整合 → 内容创作 → 质量审核
3. 输出完整的小说设定和首章内容

### 续写已有小说
1. 调用 `deepseek-html-processor` 提取历史内容
2. 调用 `storyline-organizer` 整理故事线
3. 调用 `novel-continuer` 续写内容
4. 调用 `coherence-checker` 审核连贯性

## 项目成果

- 支持生成连贯的万字级小说内容
- 保持人物性格一致性和情节逻辑严密
- 建立了可复用的智能体配置模板和协作流程
- 产出完整的使用教程和项目文档

## 开发者

独立开发者 - 2025.01 - 2025.03
