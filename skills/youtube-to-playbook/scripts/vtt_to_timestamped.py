#!/usr/bin/env python3
"""
VTT → 타임스탬프 보존 클린 텍스트 변환기.

Usage:
  vtt_to_timestamped.py <input.vtt> <output.txt>

Output format (one line per unique caption block):
  [MM:SS] text content

Features:
- Deduplicates overlapping/repeated caption lines
- Preserves start timestamp for each unique block
- Strips HTML tags from VTT cue text
- Handles both HH:MM:SS.mmm and MM:SS.mmm timestamp formats
"""
import re
import sys
from pathlib import Path


def parse_timestamp(ts_str: str) -> float:
    """Parse VTT timestamp string to seconds (float)."""
    ts_str = ts_str.strip()
    parts = ts_str.replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    elif len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    return 0.0


def seconds_to_mmss(sec: float) -> str:
    s = int(round(sec))
    return f"{s // 60:02d}:{s % 60:02d}"


def strip_tags(text: str) -> str:
    """Remove VTT/HTML tags like <c>, <b>, <00:00:01.000>."""
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def vtt_to_timestamped(vtt_path: str, out_path: str) -> None:
    text = Path(vtt_path).read_text(encoding='utf-8')

    # Split into cue blocks (separated by blank lines)
    blocks = re.split(r'\n{2,}', text)

    lines_out = []
    prev_clean = ''

    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Skip WEBVTT header and NOTE blocks
        if block.startswith('WEBVTT') or block.startswith('NOTE') \
                or block.startswith('STYLE') or block.startswith('Kind:') \
                or block.startswith('Language:'):
            continue

        block_lines = block.split('\n')

        # Find timestamp line
        ts_line = None
        ts_idx = -1
        for i, ln in enumerate(block_lines):
            if '-->' in ln:
                ts_line = ln
                ts_idx = i
                break

        if ts_line is None:
            continue

        # Parse start timestamp
        start_str = ts_line.split('-->')[0].strip()
        # Remove position/alignment settings if present
        start_str = start_str.split()[0]
        try:
            start_sec = parse_timestamp(start_str)
        except (ValueError, IndexError):
            continue

        # Collect cue text (lines after timestamp)
        cue_lines = block_lines[ts_idx + 1:]
        cue_text = ' '.join(strip_tags(ln) for ln in cue_lines if ln.strip())
        cue_text = cue_text.strip()

        if not cue_text:
            continue

        # Deduplicate: skip if identical to previous
        if cue_text == prev_clean:
            continue

        # Partial overlap dedup: skip if new text is just prev + a few chars
        # (rolling caption style produces many near-duplicates)
        if prev_clean and cue_text.startswith(prev_clean):
            # Update: replace previous entry with longer version
            if lines_out:
                ts_tag = lines_out[-1].split(']')[0] + ']'
                lines_out[-1] = f"{ts_tag} {cue_text}"
            prev_clean = cue_text
            continue

        mmss = seconds_to_mmss(start_sec)
        lines_out.append(f"[{mmss}] {cue_text}")
        prev_clean = cue_text

    Path(out_path).write_text('\n'.join(lines_out) + '\n', encoding='utf-8')
    print(f">> {len(lines_out)} caption blocks written to {out_path}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: vtt_to_timestamped.py <input.vtt> <output.txt>")
        sys.exit(1)
    vtt_to_timestamped(sys.argv[1], sys.argv[2])
