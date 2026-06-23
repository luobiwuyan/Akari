# 简化版的 puzzle_loader.py
import os
import sys
from pathlib import Path


def load_all_puzzles_from_folder(folder_path="puzzles"):
    """加载所有谜题文件的简单版本"""
    puzzle_list = []

    print(f"当前工作目录: {os.getcwd()}")
    print(f"查找谜题文件夹: {os.path.abspath(folder_path)}")

    # 确保文件夹存在
    if not os.path.exists(folder_path):
        print(f"错误: 文件夹 '{folder_path}' 不存在")
        return puzzle_list

    # 获取所有.py文件
    puzzle_files = []
    for file in os.listdir(folder_path):
        if file.endswith('.py') and file != '__init__.py':
            puzzle_files.append(os.path.join(folder_path, file))

    print(f"找到 {len(puzzle_files)} 个谜题文件")

    for file_path in puzzle_files:
        print(f"处理文件: {os.path.basename(file_path)}")

        try:
            # 直接执行文件获取数据
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 创建局部命名空间
            local_vars = {}
            exec(content, {}, local_vars)

            # 获取谜题数据
            puzzle_data = local_vars.get('PUZZLE_DATA')
            meta_info = local_vars.get('META_INFO', {})

            if puzzle_data is not None:
                puzzle_name = meta_info.get('name', os.path.basename(file_path).replace('.py', ''))
                puzzle_list.append((puzzle_name, puzzle_data, meta_info))
                print(f"✓ 加载成功: {puzzle_name}")
            else:
                print(f"⚠ 未找到PUZZLE_DATA: {file_path}")

        except Exception as e:
            print(f"✗ 加载失败 {file_path}: {e}")

    return puzzle_list


# 当被导入时自动加载
ALL_PUZZLES = load_all_puzzles_from_folder()