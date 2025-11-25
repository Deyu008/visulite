# VisuLite

交互式科研数据可视化与导出工具，基于 PySide6 + Matplotlib 构建。目标是为 CSV/TSV/Excel/JSON 数据提供「即开即用」的浏览、预处理与制图体验。

## 功能特点

### 数据导入

- 📁 多格式数据导入（CSV/TSV/Excel/JSON）
- 🔤 自动编码检测（UTF-8/GBK/UTF-16 等）
- 📋 自动生成字段统计与缺失值报告
- 🕐 最近文件快速访问（记录最近 5 个文件）

### 数据预处理

- 📊 数据表格展示，支持点击列头排序
- ✂️ 数据截取（选取前 N 行）
- 🔄 列类型转换（字符串/整数/浮点数/日期时间）
- 🔍 文本关键词筛选与数值范围过滤
- 🩹 缺失值处理（均值/中位数/0/前向/后向填充）

### 图表可视化

- 📈 基础图表（折线图/柱状图/散点图/直方图）
- 📊 扩展图表（箱线图/热力图）
- 🎨 图表控制参数：
  - 线型选择（实线/虚线/点划线）
  - 点样式选择（圆形/叉号/加号/方形/三角形/菱形）
  - 颜色方案（自动配色或自定义颜色）
  - 图例与网格显示控制
  - 坐标轴标签自定义
- 🔧 Matplotlib 交互工具栏（缩放/平移/重置视图）

### 导出功能

- 💾 多格式导出（PNG/JPG/SVG/PDF）
- ⚙️ DPI 设置（72-1200）
- 📐 自定义图表尺寸
- 📝 文件命名模板（支持 `{xcol}-{ycol}`、`figure-{timestamp}` 格式）
- 🔄 批量绘图（对文件夹内所有数据文件应用相同配置）

### 配置管理

- ⚙️ 图表配置保存/加载（JSON 格式）
- 🔁 批量复用图表设置

## 快速开始

```bash
conda activate visulite
pip install -r requirements.txt
python main.py
```

## 项目结构

```
visulite/
  app.py                  # QApplication 启动封装
  common/logging.py       # 统一日志
  models/                 # AppState / ChartConfig / DataFrameModel
  services/               # 数据加载、处理、绘图、导出、配置持久化
    batch_plotter.py      # 批量绘图服务
    chart_manager.py      # 图表渲染
    config_manager.py     # 配置持久化
    data_loader.py        # 多格式数据加载
    data_processor.py     # 数据预处理
    export_manager.py     # 图表导出
    recent_files.py       # 最近文件记录
  ui/                     # MainWindow + Matplotlib canvas + 工具栏
main.py                   # 入口
VisuLite_SRS.md           # 需求文档
```

## 开发指南

- 遵循模块边界：UI 只负责交互，其余逻辑注入到 services 层。
- 所有新服务请配置日志命名空间 `visulite.<module>`，方便排查。
- 新增图表类型时，扩展 `ChartManager.SUPPORTED_TYPES` 并更新 UI 下拉框。

## 许可证

稍后发布于 GitHub 时可选择 MIT/Apache-2.0 等宽松许可证。
