# 🐍 Python 文件清单生成器

这个脚本可以自动扫描文件夹中的 Python 文件，生成带选择框的 Markdown 清单，并支持增量更新和状态保持。

## ✨ 功能特点

- 📁 **自动扫描** Python 文件
- ☑️ **选择框清单** 支持勾选/取消勾选
- 🔄 **增量更新** 保持现有选择状态
- 🆕 **新增标记** 自动标记新文件
- ❌ **删除标记** 用删除线标记消失的文件
- 💾 **自动备份** 更新前创建备份文件
- 👀 **监控模式** 实时监控文件变化

## 🚀 快速开始

### 基本使用

```bash
# 在当前目录生成清单
python3 generate_py_checklist.py .

# 在指定目录生成清单
python3 generate_py_checklist.py /path/to/your/python/files

# 指定输出文件名
python3 generate_py_checklist.py . -o my_checklist.md
```

### 便捷脚本

```bash
# 使用便捷脚本（自动使用上级目录）
./update_py_checklist.sh

# 指定目录
./update_py_checklist.sh /path/to/directory
```

### 监控模式

```bash
# 每10秒检查一次文件变化
python3 generate_py_checklist.py . --watch

# 自定义检查间隔（5秒）
python3 generate_py_checklist.py . --watch --interval 5
```

## 📋 生成的清单格式

```markdown
# 🐍 Python 文件清单

> **文件夹**: `/path/to/files`
> **更新时间**: 2025-08-01 22:31:17

## 📊 统计信息

- 📁 **当前文件**: 11 个
- 🆕 **新增文件**: 1 个
- ❌ **消失文件**: 0 个

## ✅ 当前文件

- [x] important_script.py
- [ ] utility_functions.py
- [ ] new_feature.py 🆕

## ❌ 消失的文件

- [x] ~~old_script.py~~
```

## 🔧 高级选项

### 命令行参数

```
usage: generate_py_checklist.py [-h] [-o OUTPUT] [--watch] [--interval INTERVAL] directory

参数说明:
  directory              要扫描的目录路径
  -o, --output          输出文件名 (默认: python_files_checklist.md)
  --watch               监控模式：持续监控目录变化并自动更新清单
  --interval            监控模式下的检查间隔（秒）(默认: 10)
```

### 使用示例

```bash
# 基本用法
python3 generate_py_checklist.py src/

# 指定输出文件
python3 generate_py_checklist.py src/ -o project_files.md

# 监控模式，每5秒检查一次
python3 generate_py_checklist.py src/ --watch --interval 5
```

## 🎯 使用场景

1. **项目管理** - 跟踪项目中的 Python 文件状态
2. **代码审查** - 标记已审查的文件
3. **任务清单** - 将文件作为待办事项管理
4. **文档生成** - 自动生成项目文件清单
5. **版本控制** - 跟踪文件的添加和删除

## 📝 注意事项

- 清单文件会自动创建备份（.md.backup）
- 请勿手动修改清单文件的格式，只修改选择框状态
- 监控模式下按 Ctrl+C 退出
- 脚本只扫描直接位于指定目录下的 .py 文件（不包括子目录）

## 🔄 更新逻辑

1. **首次运行**: 扫描所有 Python 文件，默认全部未选中
2. **再次运行**: 
   - 保持现有文件的选择状态
   - 新增文件标记为 🆕，默认未选中
   - 消失的文件用删除线标记，保持原选择状态
3. **备份机制**: 每次更新前自动创建备份文件

## 📄 文件结构

```
project/
├── generate_py_checklist.py      # 主脚本
├── update_py_checklist.sh        # 便捷脚本
└── python_files_checklist.md     # 生成的清单（示例）
```

---

*Created by Python File Checklist Generator*
