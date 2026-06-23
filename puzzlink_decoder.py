#!/usr/bin/env python3
"""
decode_pzplus.py
✅ 直接在 PyCharm 控制台输入 puzz.link 链接
✅ 自动输出 puzzle 文件内容（可直接复制保存为 puzzles/xxx.py）
"""

import re
import datetime

# ==================== 核心解码逻辑 ====================
DICT = {
    '.': [-1],
    '0': [0], '1': [1], '2': [2], '3': [3], '4': [4],
    '5': [0, 5], '6': [1, 5], '7': [2, 5], '8': [3, 5], '9': [4, 5],
    'a': [0, 5, 5], 'b': [1, 5, 5], 'c': [2, 5, 5],
    'd': [3, 5, 5], 'e': [4, 5, 5],
}
for i in range(20):
    DICT[chr(i + 103)] = [5] * (i + 1)

RE = re.compile(r'https://puzz\.link/p\?akari/(?P<w>\d+)/(?P<h>\d+)/(?P<data>\S+)')


def decode_raw(s: str) -> list[int]:
    """将编码串展开为一维数字列表"""
    ret = []
    for ch in s:
        if ch not in DICT:
            raise ValueError(f"❌ 非法字符: {ch!r} (ord={ord(ch)})")
        ret.extend(DICT[ch])
    return ret


def decode_match(match: re.Match) -> list[list[int]]:
    """从正则匹配结果生成棋盘"""
    w = int(match.group('w'))
    h = int(match.group('h'))
    data = decode_raw(match.group('data'))

    if len(data) < w * h:
        raise ValueError(f"❌ 数据长度不足: {len(data)} < {w*h}")

    data = data[:w * h]
    return [data[i * w:(i + 1) * w] for i in range(h)]


def decode_from_puzzlink(url: str) -> tuple[str, list[list[int]]] | None:
    """主入口：传入 URL，返回 (尺寸字符串, 棋盘)"""
    match = RE.match(url)
    if not match:
        return None
    w = int(match.group('w'))
    h = int(match.group('h'))
    grid = decode_match(match)
    return f"{w}x{h}", grid


# ==================== 输出格式化 ====================
def format_puzzle_file(grid: list[list[int]], name: str = "imported") -> str:
    """生成完整的 puzzle 文件内容"""
    rows = len(grid)
    cols = len(grid[0])
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = []
    lines.append(f"# 自动生成: {ts}")
    lines.append(f"# 棋盘大小: {rows}×{cols}")
    lines.append("")
    lines.append("PUZZLE_DATA = [")
    for row in grid:
        lines.append("    " + repr(row) + ",")
    lines.append("]")
    lines.append("")
    lines.append("META_INFO = {")
    lines.append(f'    "name": "{name}",')
    lines.append(f'    "difficulty": "imported",')
    lines.append(f'    "size": ({rows}, {cols}),')
    lines.append(f'    "creator": "pzplus decoder",')
    lines.append(f'    "description": "",')
    lines.append("}")
    return "\n".join(lines)


# ==================== PyCharm 控制台输入 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("  🎮 Akari Puzz.link 解码器（PyCharm 专用）")
    print("=" * 60)
    print("👉 请粘贴 puzz.link 链接，然后按回车：")
    print("   示例：https://puzz.link/p?akari/17/17/xxxxxx")
    print("-" * 60)

    # ✅ 直接在控制台输入
    url = input("🔗 请输入 puzz.link 链接：").strip()

    if not url:
        print("❌ 未输入链接，程序退出")
        exit(1)

    result = decode_from_puzzlink(url)
    if not result:
        print("❌ 链接格式错误！请确保是：")
        print("   https://puzz.link/p?akari/宽度/高度/编码串")
        exit(1)

    size_str, grid = result

    print("\n" + "=" * 60)
    print(f"✅ 解码成功！棋盘尺寸：{size_str}")
    print("=" * 60)
    print("\n📋 请复制以下内容，保存为 puzzles/xxx.py：\n")

    # ✅ 直接输出 puzzle 文件内容
    puzzle_content = format_puzzle_file(grid, name=f"akari_{size_str}")
    print(puzzle_content)

    print("\n" + "=" * 60)
    print("💡 提示：")
    print("   1. 新建文件 puzzles/xxx.py")
    print("   2. 粘贴以上内容")
    print("   3. 在 gui.py 中即可加载该谜题")
    print("=" * 60)