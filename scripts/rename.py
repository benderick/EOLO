"""
将某个文件夹下的所有py文件重命名：
1. 将文件名中的空格替换为下划线
2. 以_开头
3. 将涉及的非数字，字母，下划线内容用下划线替换，但是最后的扩展名.py里的.保留
4. 如果有连续的下划线，则替换为一个下划线
"""

import os
import re

def process_filename(filename):
    """
    处理文件名，按照指定规则进行重命名
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 处理后的文件名
    """
    # 分离文件名和扩展名
    name, ext = os.path.splitext(filename)
    
    # 特殊处理：先处理版本号格式（在空格替换之前）
    def format_version_numbers(text):
        """
        将文本中的版本号格式化为三位数
        例：91.0 -> 091, 66.0 -> 066, 1 -> 001
        """
        # 第一步：处理数字.0格式，直接替换为补零的数字
        def replace_decimal_zero(match):
            num_str = match.group(1)
            return num_str.zfill(3)  # 补零到3位数
        
        # 匹配并替换 数字.0 格式（包括前后的空格或其他分隔符）
        text = re.sub(r'(\d+)\.0(?=\s|$|[^0-9.])', replace_decimal_zero, text)
        
        return text
    
    # 先应用版本号格式化
    name = format_version_numbers(name)
    
    # 1. 将空格替换为下划线
    name = name.replace(' ', '_')
    
    # 处理剩余的独立数字
    def format_remaining_numbers(text):
        """
        处理剩余的独立数字，补零到3位数
        """
        def replace_standalone_number(match):
            num_str = match.group(0)
            # 只对1-2位数字进行补零处理
            if len(num_str) <= 2:
                return num_str.zfill(3)
            return num_str
        
        # 匹配独立的1-2位数字（前后是非数字字符或边界）
        text = re.sub(r'\b\d{1,2}\b', replace_standalone_number, text)
        
        return text
    
    # 应用剩余数字格式化
    name = format_remaining_numbers(name)
    
    # 3. 将非数字、字母、下划线的字符替换为下划线（保留扩展名中的点）
    name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # 2. 确保以下划线开头
    if not name.startswith('_'):
        name = '_' + name
    
    # 4. 将连续的下划线替换为单个下划线
    name = re.sub(r'_{2,}', '_', name)
    
    # 返回处理后的完整文件名
    return name + ext

def rename_py_files(directory):
    """
    重命名指定目录下的所有.py文件
    
    Args:
        directory (str): 目标目录路径
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        print(f"错误：目录 '{directory}' 不存在")
        return
    
    # 获取目录下所有.py文件
    py_files = [f for f in os.listdir(directory) if f.endswith('.py')]
    
    if not py_files:
        print(f"目录 '{directory}' 下没有找到.py文件")
        return
    
    print(f"在目录 '{directory}' 中找到 {len(py_files)} 个.py文件")
    
    # 处理每个.py文件
    for filename in py_files:
        old_path = os.path.join(directory, filename)
        new_filename = process_filename(filename)
        new_path = os.path.join(directory, new_filename)
        
        # 如果新文件名与原文件名相同，跳过
        if filename == new_filename:
            print(f"跳过：'{filename}' (无需重命名)")
            continue
        
        # 检查新文件名是否已存在
        if os.path.exists(new_path):
            print(f"警告：'{new_filename}' 已存在，跳过重命名 '{filename}'")
            continue
        
        try:
            # 执行重命名操作
            os.rename(old_path, new_path)
            print(f"重命名：'{filename}' -> '{new_filename}'")
        except OSError as e:
            print(f"错误：无法重命名 '{filename}'，原因：{e}")

def main():
    """
    主函数，获取用户输入的目录路径并执行重命名操作
    """
    # 获取用户输入的目录路径
    directory = input("请输入要处理的目录路径：").strip()
    
    # 如果用户没有输入，使用当前目录
    if not directory:
        directory = os.getcwd()
        print(f"使用当前目录：{directory}")
    
    # 执行重命名操作
    rename_py_files(directory)
    print("重命名操作完成！")

if __name__ == "__main__":
    main()

