#!/usr/bin/env python3
"""把 stage 文件内容替换进目标文件的 [start, end] 闭区间行（1-based，含首尾）。"""
import sys

target, stage, start, end = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
lines = open(target, encoding='utf-8').read().split('\n')
new = open(stage, encoding='utf-8').read().split('\n')
while new and new[-1] == '':
    new.pop()
assert 1 <= start <= end <= len(lines), f'range out of bounds: {start}-{end}/{len(lines)}'
old = lines[start - 1:end]
lines[start - 1:end] = new
open(target, 'w', encoding='utf-8').write('\n'.join(lines))
print(f'replaced lines {start}-{end} ({len(old)} -> {len(new)})')
print('first old:', old[0][:70])
print('last  old:', old[-1][:70])