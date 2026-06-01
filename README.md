# ☯ 命理学结构化决策分析

从中国传统命理学（八字、五行、十神、大运）中提取结构化分析思维，去掉玄学宣称，改造成现代决策分析工具。

## 核心思想

| 命理学概念 | 现代决策对应 |
|---|---|
| 八字（年月日时）| 四维情境编码（环境/局势/自身/目标）|
| 五行（金木水火土）| 五种抽象力量（创造/表现/稳定/决断/流动）|
| 生克关系 | 资源间的促进/制约网络 |
| 十神 | 利益相关者角色映射 |
| 大运流年 | 时间阶段动态推演 |

## 五要素

| 力量 | 命理对应 | 现代含义 |
|---|---|---|
| 🌳 木 | 生长力 | 创造力、新想法、扩张、突破 |
| 🔥 火 | 表现力 | 影响力、展示、沟通、感染力 |
| 🏔 土 | 承载力 | 稳定性、基础、信任、持久 |
| ⚔️ 金 | 收敛力 | 决断、规则、纪律、取舍 |
| 💧 水 | 流动力 | 信息、人脉、适应、资源调配 |

## 使用方式

### Web版（推荐）
```bash
pip install fastapi uvicorn pydantic
python app.py
# 访问 http://localhost:8088
```

### Python API
```python
from app import *

sit = Situation(
    question="要不要跳槽？",
    dimensions=[
        Dimension(Pillar.YEAR, Element.WATER, 7, "经济环境不确定"),
        Dimension(Pillar.MONTH, Element.METAL, 8, "大厂天花板明显"),
        Dimension(Pillar.DAY, Element.WOOD, 7, "有创造力想做事"),
        Dimension(Pillar.HOUR, Element.FIRE, 6, "想要更大影响力"),
    ],
)

az = MetaphorAnalyzer(sit)
report, data = az.full_report()
print(report)
```

## 分析维度

1. **五要素平衡** — 类比八字五行旺衰，看资源分布是否均衡
2. **关系网络** — 类比生克制化，看各因素间的促进/制约
3. **角色格局** — 类比十神格局，看利益相关者配置
4. **阶段推演** — 类比大运流年，看时间节奏

## 声明

本工具**不预测未来**，不具有任何超自然能力。

它只是借用命理学的**结构化分析框架**来辅助决策，本质上与 SWOT 分析、OODA 循环等现代决策工具类似。
