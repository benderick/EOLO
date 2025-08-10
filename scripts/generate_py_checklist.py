#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 文件清单生成器
自动扫描文件夹下的 Python 文件，生成带选择框的 Markdown 清单
支持增量更新，保持原有选择状态，标记删除的文件
"""

import os
import re
from pathlib import Path
from typing import Dict, Set, List
from datetime import datetime

class PyFileChecklistGenerator:
    """Python 文件清单生成器"""
    
    def __init__(self, target_dir: str, output_file: str = "python_files_checklist.md"):
        """
        初始化生成器
        
        Args:
            target_dir: 目标文件夹路径
            output_file: 输出的 Markdown 文件名
        """
        self.target_dir = Path(target_dir).resolve()
        self.output_file = Path(output_file)
        
        # 如果输出文件路径不是绝对路径，则相对于目标目录
        if not self.output_file.is_absolute():
            self.output_file = self.target_dir / self.output_file
            
        # 正则表达式：匹配复选框行
        # 格式：- [x] filename.py 或 - [ ] filename.py
        self.checkbox_pattern = re.compile(r'^- \[([ x])\] (.+?)$', re.MULTILINE)
        
        # 正则表达式：匹配删除线的复选框行
        # 格式：- [x] ~~filename.py~~
        self.strikethrough_pattern = re.compile(r'^- \[([ x])\] ~~(.+?)~~$', re.MULTILINE)
    
    def scan_python_files(self) -> Set[str]:
        """
        扫描目标文件夹下的所有 Python 文件
        
        Returns:
            Set[str]: Python 文件名集合
        """
        python_files = set()
        
        try:
            if not self.target_dir.exists():
                print(f"❌ 目标文件夹不存在: {self.target_dir}")
                return python_files
                
            if not self.target_dir.is_dir():
                print(f"❌ 指定路径不是文件夹: {self.target_dir}")
                return python_files
            
            # 扫描所有 .py 文件
            for file_path in self.target_dir.glob("*.py"):
                if file_path.is_file():
                    python_files.add(file_path.name)
                    
            print(f"📁 扫描到 {len(python_files)} 个 Python 文件")
            return python_files
            
        except Exception as e:
            print(f"❌ 扫描文件时发生错误: {e}")
            return python_files
    
    def parse_existing_checklist(self) -> Dict[str, bool]:
        """
        解析现有的 Markdown 清单文件
        
        Returns:
            Dict[str, bool]: 文件名到选择状态的映射
        """
        file_states = {}
        
        if not self.output_file.exists():
            print("📝 未找到现有清单文件，将创建新文件")
            return file_states
        
        try:
            with open(self.output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析普通的复选框条目（排除新增标记和删除线）
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                # 匹配格式: - [x] filename.py 或 - [ ] filename.py 🆕
                match = re.match(r'^- \[([ x])\] (.+?)(?:\s+🆕)?$', line)
                if match and not ('~~' in line):  # 排除删除线标记的行
                    checked, filename = match.groups()
                    # 移除可能的新增标记
                    filename = filename.replace(' 🆕', '').strip()
                    file_states[filename] = (checked == 'x')
            
            # 解析删除线标记的条目
            strikethrough_matches = self.strikethrough_pattern.findall(content)
            for checked, filename in strikethrough_matches:
                # 移除可能的新增标记
                filename = filename.replace(' 🆕', '').strip()
                file_states[filename] = (checked == 'x')
            
            print(f"📖 解析现有清单: 找到 {len(file_states)} 个文件的状态记录")
            
        except Exception as e:
            print(f"⚠️ 解析现有清单文件时发生错误: {e}")
            
        return file_states
    
    def categorize_files(self, current_files: Set[str], existing_states: Dict[str, bool]) -> Dict[str, List[str]]:
        """
        对文件进行分类
        
        Args:
            current_files: 当前存在的文件集合
            existing_states: 现有的文件状态映射
            
        Returns:
            Dict[str, List[str]]: 分类后的文件字典
        """
        # 获取历史记录中的所有文件
        historical_files = set(existing_states.keys())
        
        categorized = {
            'current': sorted(list(current_files)),  # 当前存在的文件
            'new': sorted(list(current_files - historical_files)),  # 新增的文件
            'missing': sorted(list(historical_files - current_files))  # 消失的文件
        }
        
        print(f"📊 文件分类统计:")
        print(f"   - 当前文件: {len(categorized['current'])} 个")
        print(f"   - 新增文件: {len(categorized['new'])} 个")
        print(f"   - 消失文件: {len(categorized['missing'])} 个")
        
        return categorized
    
    def generate_markdown_content(self, categorized_files: Dict[str, List[str]], 
                                existing_states: Dict[str, bool]) -> str:
        """
        生成 Markdown 内容
        
        Args:
            categorized_files: 分类后的文件字典
            existing_states: 现有的文件状态映射
            
        Returns:
            str: 生成的 Markdown 内容
        """
        lines = []
        
        # 文件头部
        lines.append("# 🐍 Python 文件清单")
        lines.append("")
        lines.append(f"> **文件夹**: `{self.target_dir}`")
        lines.append(f"> **更新时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        # 统计信息
        lines.append("## 📊 统计信息")
        lines.append("")
        lines.append(f"- 📁 **当前文件**: {len(categorized_files['current'])} 个")
        lines.append(f"- 🆕 **新增文件**: {len(categorized_files['new'])} 个")
        lines.append(f"- ❌ **消失文件**: {len(categorized_files['missing'])} 个")
        lines.append("")
        
        # 当前文件列表
        if categorized_files['current']:
            lines.append("## ✅ 当前文件")
            lines.append("")
            
            for filename in categorized_files['current']:
                # 获取文件的选择状态，新文件默认未选择
                is_checked = existing_states.get(filename, False)
                checkbox = '[x]' if is_checked else '[ ]'
                
                # 标记新文件
                if filename in categorized_files['new']:
                    lines.append(f"- {checkbox} {filename} 🆕")
                else:
                    lines.append(f"- {checkbox} {filename}")
            
            lines.append("")
        
        # 消失的文件列表（用删除线标记）
        if categorized_files['missing']:
            lines.append("## ❌ 消失的文件")
            lines.append("")
            lines.append("*以下文件在历史记录中存在，但当前文件夹中已不存在*")
            lines.append("")
            
            for filename in categorized_files['missing']:
                # 保持原有的选择状态
                is_checked = existing_states.get(filename, False)
                checkbox = '[x]' if is_checked else '[ ]'
                lines.append(f"- {checkbox} ~~{filename}~~")
            
            lines.append("")
        
        # 说明信息
        lines.append("---")
        lines.append("")
        lines.append("### 📝 使用说明")
        lines.append("")
        lines.append("- ✅ 选中的复选框表示该文件已被标记")
        lines.append("- 🆕 标记表示新增的文件")
        lines.append("- ~~删除线~~ 表示文件已不存在于当前文件夹中")
        lines.append("- 重新运行脚本会保持现有的选择状态")
        lines.append("")
        lines.append("*此文件由脚本自动生成，请勿手动修改格式*")
        
        return '\n'.join(lines)
    
    def save_checklist(self, content: str) -> bool:
        """
        保存清单到文件
        
        Args:
            content: 要保存的内容
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 如果文件已存在，创建备份
            if self.output_file.exists():
                backup_path = self.output_file.with_suffix('.md.backup')
                self.output_file.rename(backup_path)
                print(f"💾 创建备份文件: {backup_path}")
            
            # 确保输出目录存在
            self.output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存新内容
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ 清单已保存到: {self.output_file}")
            return True
            
        except Exception as e:
            print(f"❌ 保存文件时发生错误: {e}")
            return False
    
    def generate(self) -> bool:
        """
        生成或更新文件清单
        
        Returns:
            bool: 是否成功生成
        """
        print(f"🚀 开始生成 Python 文件清单...")
        print(f"📂 目标文件夹: {self.target_dir}")
        print(f"📄 输出文件: {self.output_file}")
        
        # 1. 扫描当前文件
        current_files = self.scan_python_files()
        if not current_files:
            print("⚠️ 未找到任何 Python 文件")
            return False
        
        # 2. 解析现有清单
        existing_states = self.parse_existing_checklist()
        
        # 3. 分类文件
        categorized_files = self.categorize_files(current_files, existing_states)
        
        # 4. 生成 Markdown 内容
        content = self.generate_markdown_content(categorized_files, existing_states)
        
        # 5. 保存文件
        success = self.save_checklist(content)
        
        if success:
            print("🎉 文件清单生成完成！")
        
        return success

def main():
    """主函数"""
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(
        description="生成 Python 文件清单，支持增量更新和状态保持",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  %(prog)s .                              # 在当前目录生成清单
  %(prog)s /path/to/folder                # 在指定目录生成清单
  %(prog)s . -o my_checklist.md          # 指定输出文件名
  %(prog)s /path/to/folder --watch        # 监控模式（每10秒检查一次）
        """
    )
    
    parser.add_argument(
        'directory',
        help='要扫描的目录路径'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='python_files_checklist.md',
        help='输出文件名 (默认: python_files_checklist.md)'
    )
    
    parser.add_argument(
        '--watch',
        action='store_true',
        help='监控模式：持续监控目录变化并自动更新清单'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=10,
        help='监控模式下的检查间隔（秒）(默认: 10)'
    )
    
    args = parser.parse_args()
    
    # 验证目录
    if not os.path.exists(args.directory):
        print(f"❌ 目录不存在: {args.directory}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"❌ 指定路径不是目录: {args.directory}")
        sys.exit(1)
    
    # 创建生成器
    generator = PyFileChecklistGenerator(args.directory, args.output)
    
    if args.watch:
        # 监控模式
        import time
        import signal
        
        print(f"👀 进入监控模式，每 {args.interval} 秒检查一次文件变化")
        print("按 Ctrl+C 退出监控...")
        
        def signal_handler(signum, frame):
            print("\n🛑 退出监控模式")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        last_files = set()
        try:
            while True:
                current_files = generator.scan_python_files()
                if current_files != last_files:
                    print(f"\n🔍 检测到文件变化，正在更新清单...")
                    generator.generate()
                    last_files = current_files
                else:
                    print(".", end="", flush=True)
                
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n🛑 监控已停止")
    else:
        # 单次生成模式
        success = generator.generate()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
