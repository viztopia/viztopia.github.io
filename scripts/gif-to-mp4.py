#!/usr/bin/env python3
"""Convert heavy GIFs to looping MP4s and rewrite HTML references.

Requires ffmpeg on PATH. Run from the repo root:
    python3 scripts/gif-to-mp4.py            # dry run, lists what would change
    python3 scripts/gif-to-mp4.py --apply    # actually convert + rewrite

Skips GIFs smaller than --min-mb (default 3 MB). Replaces:
    <img ...src="foo.gif" alt="X" ...>
with:
    <video autoplay loop muted playsinline ...src="foo.mp4">
preserving any width/height/style/class attrs and adding poster=foo.gif's first
frame is not extracted — keeping it simple.
"""
import argparse, glob, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_gifs(min_bytes: int):
    out = []
    for path in glob.glob(os.path.join(ROOT, 'images', '**', '*.gif'), recursive=True):
        sz = os.path.getsize(path)
        if sz >= min_bytes:
            out.append((sz, path))
    out.sort(reverse=True)
    return out


def html_files():
    return sorted(glob.glob(os.path.join(ROOT, '*.html')))


def convert(gif_path: str) -> str:
    mp4_path = gif_path[:-4] + '.mp4'
    # libx264 with even-dim crop (yuv420p needs even); -movflags +faststart for web.
    cmd = [
        'ffmpeg', '-y', '-i', gif_path,
        '-movflags', '+faststart',
        '-pix_fmt', 'yuv420p',
        '-vf', 'crop=trunc(iw/2)*2:trunc(ih/2)*2',
        '-c:v', 'libx264',
        '-crf', '23',
        '-preset', 'slow',
        '-an',
        mp4_path,
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mp4_path


# Replace <img ...src="X.gif"...> with a <video> tag preserving the other attrs.
IMG_RE = re.compile(
    r'<img\b([^>]*?)\bsrc="([^"]+\.gif)"([^>]*)>',
    re.IGNORECASE,
)


def rewrite_html(path: str, gif_basenames_done: set) -> int:
    with open(path) as f:
        txt = f.read()
    n = 0

    def repl(m):
        nonlocal n
        pre, src, post = m.group(1), m.group(2), m.group(3)
        if os.path.basename(src) not in gif_basenames_done:
            return m.group(0)
        new_src = src[:-4] + '.mp4'
        # Strip alt="..." since <video> uses inner content for accessibility; keep loading attr if present.
        attrs = (pre + post)
        attrs = re.sub(r'\s*alt="[^"]*"', '', attrs)
        n += 1
        return f'<video autoplay loop muted playsinline{attrs} src="{new_src}"></video>'

    new_txt = IMG_RE.sub(repl, txt)
    if new_txt != txt:
        with open(path, 'w') as f:
            f.write(new_txt)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--min-mb', type=float, default=3.0,
                    help='Skip GIFs smaller than this many MB (default 3)')
    ap.add_argument('--apply', action='store_true',
                    help='Actually convert and rewrite (otherwise dry run)')
    ap.add_argument('--keep-gif', action='store_true',
                    help='Leave the original .gif on disk (default: delete after conversion)')
    args = ap.parse_args()

    if args.apply and not shutil.which('ffmpeg'):
        sys.exit('ffmpeg not found on PATH. Install it (brew install ffmpeg / apt install ffmpeg).')

    gifs = find_gifs(int(args.min_mb * 1024 * 1024))
    if not gifs:
        print('No GIFs above threshold.')
        return

    print(f'{len(gifs)} GIF(s) >= {args.min_mb} MB:')
    for sz, p in gifs:
        rel = os.path.relpath(p, ROOT)
        print(f'  {sz/1024/1024:>6.1f} MB  {rel}')

    if not args.apply:
        print('\n(dry run — pass --apply to convert + rewrite HTML)')
        return

    converted = set()
    saved = 0
    for sz, p in gifs:
        rel = os.path.relpath(p, ROOT)
        try:
            mp4 = convert(p)
        except subprocess.CalledProcessError as e:
            print(f'  FAIL  {rel}: {e}')
            continue
        new_sz = os.path.getsize(mp4)
        saved += sz - new_sz
        print(f'  ok    {rel}: {sz/1024/1024:.1f} MB -> {new_sz/1024/1024:.1f} MB')
        converted.add(os.path.basename(p))
        if not args.keep_gif:
            os.remove(p)

    print(f'\nTotal saved: {saved/1024/1024:.1f} MB')
    print('Rewriting HTML references...')
    total = 0
    for h in html_files():
        n = rewrite_html(h, converted)
        if n:
            print(f'  {os.path.basename(h)}: {n} <img> -> <video>')
            total += n
    print(f'\nDone. {total} tag(s) rewritten across {len(html_files())} pages.')


if __name__ == '__main__':
    main()
