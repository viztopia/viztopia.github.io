#!/usr/bin/env python3
"""Convert images/about/ygs/*.jpg → .webp and update wave600.json paths.
Uses 8 parallel workers. Safe to re-run (skips already-converted files).
Run from repo root: python3 scripts/convert-ygs-webp.py
"""
import os, json, subprocess
from multiprocessing.pool import ThreadPool

WEBP_Q   = 82
REPO     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YGS_DIR  = os.path.join(REPO, 'images', 'about', 'ygs')
WAVE_JSON = os.path.join(REPO, 'js', 'about', 'wave600.json')

jpgs = sorted(
    os.path.join(YGS_DIR, f)
    for f in os.listdir(YGS_DIR)
    if f.lower().endswith('.jpg')
)
print(f'Found {len(jpgs)} JPEGs in {os.path.relpath(YGS_DIR, REPO)}')
if not jpgs:
    print('Nothing to do.')
else:
    total_before = sum(os.path.getsize(p) for p in jpgs)

    def convert_one(src):
        dst = src[:-4] + '.webp'
        if os.path.exists(dst):
            os.remove(src)
            return os.path.getsize(dst), True   # already done
        before = os.path.getsize(src)
        ret = subprocess.run(
            ['convert', src, '-quality', str(WEBP_Q), dst],
            capture_output=True
        )
        if ret.returncode != 0:
            return 0, False
        os.remove(src)
        return os.path.getsize(dst), True

    with ThreadPool(8) as pool:
        results = pool.map(convert_one, jpgs)

    ok       = sum(1 for _, s in results if s)
    total_after = sum(sz for sz, s in results if s)
    saved    = (total_before - total_after) // 1024 // 1024
    print(f'Converted {ok}/{len(jpgs)} images  '
          f'({total_before//1024//1024}MB → {total_after//1024//1024}MB, -{saved}MB)')

    # Update wave600.json
    print('Updating wave600.json ...')
    with open(WAVE_JSON, 'r') as f:
        data = json.load(f)
    changed = 0
    for item in data:
        if item['name'].endswith('.jpg'):
            item['name'] = item['name'][:-4] + '.webp'
            changed += 1
    with open(WAVE_JSON, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    print(f'Updated {changed} paths in wave600.json')

print('Done.')
