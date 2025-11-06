# SayHello Tool

一个简单的问候工具，用于演示如何将外部工具包集成到 MacroFlow。

## 功能

- 生成个性化问候语
- 支持多语言（英语、中文、西班牙语、法语）
- 批量处理功能

## 安装

```bash
# 在 MacroFlow 项目根目录运行
make prepare-sayhello
```

## 使用示例

### 在 Python 中直接使用

```python
from sayhello import sayhello

# 简单问候
result = sayhello("Alice")
print(result)  # hello Alice!
```

### 在 MacroFlow 中使用

```python
# 通过 MacroFlow 工具注册系统
from src.tools.registry import tool_registry

tool = tool_registry.get_tool("sayhello")
result = tool.func(name="Alice", language="en")
print(result)
# {'success': True, 'greeting': 'hello Alice!', ...}
```

### 通过 Agent 使用

启动 MacroFlow 交互式界面：

```bash
pixi run python main.py --interactive
```

然后输入：
- "使用 sayhello 工具向 Alice 问好"
- "用 sayhello 问候 Bob，使用中文"
- "用 sayhello_batch 批量问候 Alice、Bob 和 Charlie"

## 开发

```bash
# 安装开发依赖
cd src/tools/sayhello
uv sync

# 运行测试
uv run pytest

# 运行示例
uv run python src/sayhello/main.py
```

## 架构说明

```
sayhello/
├── src/sayhello/          # 核心实现（独立包）
│   ├── __init__.py
│   └── main.py            # 核心 sayhello 函数
├── macroflow_tool.py      # MacroFlow 集成层
├── __init__.py            # 包入口
├── pyproject.toml         # UV 依赖管理
└── README.md              # 文档
```

## 集成到 MacroFlow 的步骤

1. **创建独立工具包**：在 `src/sayhello/` 实现核心功能
2. **创建集成接口**：在 `macroflow_tool.py` 中使用 `@register_tool` 装饰器
3. **配置依赖管理**：在 `pyproject.toml` 中定义依赖
4. **更新 Makefile**：在 `src/tools/deps/Makefile` 中添加安装规则
5. **测试集成**：运行 `make prepare-sayhello` 并测试

## License

MIT

