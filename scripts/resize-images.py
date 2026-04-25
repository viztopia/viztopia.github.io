#!/usr/bin/env python3
"""Resize portfolio JPEGs wider than MAX_W to MAX_W at JPEG_Q quality, in-place.
Skips images/about/ygs/ (handled by convert-ygs-webp.py).
Run from repo root: python3 scripts/resize-images.py
"""
import os, struct, subprocess

MAX_W   = 1600   # max width in pixels (retina-safe for 800px display)
JPEG_Q  = 85
SKIP    = {'images/about/ygs', 'images/about/ygs/'}
REPO    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def jpeg_width(path):
    try:
        with open(path, 'rb') as f:
            d = f.read()
        i = 2
        while i < len(d) - 4:
            if d[i] != 0xFF:
                break
            marker = d[i + 1]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3):
                return struct.unpack('>H', d[i + 7:i + 9])[0]
            length = struct.unpack('>H', d[i + 2:i + 4])[0]
            i += 2 + length
    except Exception:
        pass
    return 0

resized   = 0
saved_kb  = 0
errors    = []

for root, dirs, files in os.walk(os.path.join(REPO, 'images')):
    rel = os.path.relpath(root, REPO).replace('\\', '/')
    if any(rel == s.rstrip('/') or rel.startswith(s) for s in SKIP):
        dirs.clear()
        continue
    for fn in sorted(files):
        if not fn.lower().endswith(('.jpg', '.jpeg')):
            continue
        fp = os.path.join(root, fn)
        w  = jpeg_width(fp)
        if w <= MAX_W:
            continue
        before = os.path.getsize(fp)
        ret = subprocess.run(
            ['convert', fp, '-resize', f'{MAX_W}x{MAX_W}>', '-quality', str(JPEG_Q), fp],
            capture_output=True
        )
        if ret.returncode != 0:
            errors.append(f'{fp}: {ret.stderr.decode().strip()}')
            continue
        after    = os.path.getsize(fp)
        saved    = before - after
        saved_kb += saved // 1024
        resized  += 1
        print(f'  {os.path.relpath(fp, REPO):60s}  {before//1024:5d}KB → {after//1024:4d}KB  (-{saved//1024}KB)')

print(f'\n{resized} images resized, ~{saved_kb//1024}MB saved.')
for e in errors:
    print(f'ERROR: {e}')
