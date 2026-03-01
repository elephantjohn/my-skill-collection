image-generator-python/
├── README.md
├── requirements.txt
├── setup.py
├── image_generator/
│   ├── __init__.py
│   ├── generator.py          # 主生成器
│   ├── selector.py           # API 选择器
│   ├── providers/
│   │   ├── __init__.py
│   │   ├── base.py           # 基础类
│   │   ├── imagen.py         # Google Imagen
│   │   └── seadream.py       # SeaDream
│   ├── utils/
│   │   ├── __init__.py
│   │   └── cost.py           # 成本追踪
│   └── config.py             # 配置管理
├── examples/
│   ├── basic.py              # 基础示例
│   ├── batch.py              # 批量生成
│   └── advanced.py           # 高级用法
└── tests/
    └── test_generator.py
