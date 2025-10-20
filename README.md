# Paper Vis - 智能论文分析系统

## 📖 项目简介

Paper Vis 是一个基于人工智能的智能论文分析系统，能够自动解析学术论文PDF文件，提取关键信息，生成结构化数据，为学术研究和论文写作提供智能支持。

## 🚀 核心功能

### 1. PDF智能解析
- **多格式支持**：支持各种学术论文PDF格式
- **内容提取**：自动提取文本、图表、参考文献等
- **结构化处理**：将非结构化内容转换为结构化数据

### 2. 摘要语步分析
- **四步式结构**：Background/Problem → Method/Approach → Result → Conclusion/Contribution
- **智能识别**：自动识别摘要中的关键信息
- **结构化输出**：生成标准化的摘要语步数据

### 3. 泳道内容提取
- **五大泳道**：Context & Related Work, Methodology & Setup, Results & Analysis, Conclusion
- **智能分类**：自动将论文内容分类到对应泳道
- **内容优化**：提取和整理关键信息

### 4. 图表映射系统
- **智能识别**：自动识别论文中的图表
- **分类映射**：将图表按泳道进行分类
- **引用分析**：分析图表在文本中的引用关系

### 5. 综合调度系统
- **端到端处理**：完整的论文分析流程
- **并行处理**：多任务并行执行，提高效率
- **结果整合**：生成包含所有信息的综合结果

## 🛠️ 技术架构

### 核心组件
- **PDFParserClient**：PDF解析客户端
- **AbstractStepsAnalyzer**：摘要语步分析器
- **LaneExtractor**：泳道内容提取器
- **FigureMapGenerator**：图表映射生成器
- **MainScheduler**：综合调度器

### 技术栈
- **Python 3.8+**
- **FastAPI**：Web API框架
- **Pydantic**：数据验证
- **异步处理**：提高系统性能
- **JSON数据格式**：标准化数据交换

## 📁 项目结构

```
paper_vis/
├── MainScheduler.py          # 综合调度器
├── AbstractSteps.py          # 摘要语步分析
├── LaneExtractor.py          # 泳道内容提取
├── FigureMapGenerator.py     # 图表映射生成
├── PDFParserClient.py        # PDF解析客户端
├── api_server.py            # API服务器
├── config.py               # 配置文件
├── requirements.txt         # 依赖管理
└── README.md               # 详细文档
```

## 🚀 快速开始

### 环境要求
- Python 3.8+
- 相关依赖包（见 requirements.txt）

### 安装步骤
1. 克隆项目
2. 安装依赖：`pip install -r requirements.txt`
3. 运行主程序：`python MainScheduler.py`

### API使用
1. 启动API服务器：`python api_server.py`
2. 访问API文档：`http://localhost:8000/docs`
3. 上传PDF文件进行分析

## 📊 处理流程

1. **PDF上传** → 文件验证和预处理
2. **内容解析** → 提取文本、图表、元数据
3. **并行分析** → 同时执行摘要、泳道、图表分析
4. **数据整合** → 生成综合结果
5. **结果输出** → 返回结构化JSON数据

## 🎯 应用场景

- **学术研究**：快速理解论文结构和内容
- **论文写作**：参考优秀论文的写作结构
- **文献综述**：批量分析相关论文
- **知识管理**：建立个人学术知识库

## 📈 性能特点

- **高效处理**：并行处理多个分析任务
- **智能识别**：基于AI的内容识别和分类
- **标准化输出**：统一的数据格式和结构
- **可扩展性**：模块化设计，易于扩展

## 🔧 配置说明

系统支持多种配置选项，包括：
- API端点配置
- 处理参数设置
- 输出格式选择
- 性能优化选项

## 📝 更新日志

- **v1.0.0**：基础功能实现
- **v1.1.0**：增加API接口
- **v1.2.0**：优化处理性能
- **v1.3.0**：完善文档和示例

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请通过GitHub Issues联系我们。

---

**Paper Vis** - 让论文分析更智能、更高效！
