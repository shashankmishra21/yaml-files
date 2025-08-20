#!/usr/bin/env python3
import os
import re

# Input/Output
# If you ran a normalizer first, set INPUT = 'routes/fetch_br_norm.yaml'
# Otherwise, point directly to your original routes file:
INPUT = 'routes/fetch_br_norm.yaml'
OUTPUT = 'dist/fetch_br_flat.yaml'

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# Common Unicode spaces that sometimes sneak in from editors/copy-paste
NBSP = '\u00A0'    # non-breaking space
FIGSP = '\u2007'   # figure space
NNBSP = '\u202F'   # narrow no-break space

def read_file(p: str) -> str:
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(p: str, s: str) -> None:
    with open(p, 'w', encoding='utf-8') as f:
        f.write(s)

def normalize_spaces(text: str) -> str:
    # Normalize known unicode spaces to regular spaces
    return text.replace(NBSP, ' ').replace(FIGSP, ' ').replace(NNBSP, ' ')

def resolve_include_path(base_dir: str, include_expr: str) -> str:
    s = include_expr.strip()
    # Optional "file:" prefix
    if s.lower().startswith('file:'):
        s = s[5:].strip()
    # Strip query params if present
    qpos = s.find('?')
    if qpos != -1:
        s = s[:qpos].strip()
    # Safety: trim stray punctuation at end
    s = s.rstrip('),')
    # Join to base dir
    return os.path.normpath(os.path.join(base_dir, s))

def indent_block(text: str, spaces: int) -> str:
    pad = ' ' * spaces
    return '\n'.join((pad + line) if line else '' for line in text.split('\n'))

# Permissive include matcher:
# - list dash
# - !include
# - optional "file:" prefix
# - capture everything after (we'll sanitize below)
INCLUDE_RE = re.compile(r'^(\s*)-\s*!include\s+(?:file:\s*)?(.+?)\s*$')

def flatten(input_file: str) -> str:
    base_dir = os.getcwd()
    src = normalize_spaces(read_file(input_file))
    lines = src.split('\n')

    out = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        m = INCLUDE_RE.match(line)

        if not m:
            out.append(line)
            i += 1
            continue

        indent = m.group(1)

        # Extract and sanitize the include target (path + optional query/comments)
        raw_target = m.group(2)  # whatever comes after !include on the same line

        # Drop any inline comments
        hash_pos = raw_target.find('#')
        if hash_pos != -1:
            raw_target = raw_target[:hash_pos]
        raw_target = raw_target.strip()

        # Strip inline query params if present
        qpos = raw_target.find('?')
        if qpos != -1:
            path_part = raw_target[:qpos].strip()
        else:
            path_part = raw_target

        # Strip an optional file: prefix if it still exists
        if path_part.lower().startswith('file:'):
            path_part = path_part[5:].strip()

        # Keep only the path ending with .yml/.yaml if additional junk is present
        m_path = re.search(r'([^\s]+\.ya?ml)', path_part)
        if m_path:
            include_rel_path = m_path.group(1)
        else:
            include_rel_path = path_part

        # Collect args: block that follows (same indent level + at least one more space)
        args_lines = []
        j = i + 1
        next_indent_re = re.compile(r'^' + re.escape(indent) + r'\s+')
        if j < n and next_indent_re.match(lines[j]) and lines[j].lstrip().startswith('args:'):
            args_lines.append(lines[j])
            j += 1
            while j < n and next_indent_re.match(lines[j]):
                args_lines.append(lines[j])
                j += 1

        # Resolve and read included file
        inc_path = resolve_include_path(base_dir, include_rel_path)
        # print(f"DEBUG resolved include: {include_rel_path} -> {inc_path} (exists={os.path.exists(inc_path)})")

        if not os.path.exists(inc_path):
            # If missing, keep original include and args block
            out.append(line)
            for a in args_lines:
                out.append(a)
            i = j
            continue

        inc_content = normalize_spaces(read_file(inc_path))
        inc_lines = inc_content.split('\n')

        # Skip leading blank lines in the included file
        first_idx = 0
        while first_idx < len(inc_lines) and not inc_lines[first_idx].strip():
            first_idx += 1

        dash = indent + '- '
        first_line = inc_lines[first_idx] if first_idx < len(inc_lines) else ''

        # If first line looks like "key:" start, inline it nicely as a list item
        if re.match(r'^\s*[\w\-\"]+\s*:', first_line):
            out.append(dash + first_line.strip())
            rest = '\n'.join(inc_lines[first_idx + 1:])
            if rest.strip():
                out.append(indent_block(rest, len(indent) + 2))
        else:
            # Fallback: include as a literal block to avoid YAML breakage
            out.append(dash + '|')
            out.append(indent_block(inc_content, len(indent) + 2))

        # Preserve args as comments (for traceability)
        if args_lines:
            out.append(indent + '  # ---- args (preserved for reference) ----')
            for a in args_lines:
                out.append(indent + '  # ' + a.strip())

        i = j

    return '\n'.join(out)

if __name__ == '__main__':
    # Ensure input exists
    if not os.path.exists(INPUT):
        print(f'❌ Input file not found: {INPUT}')
        raise SystemExit(1)

    flat = flatten(INPUT)
    write_file(OUTPUT, flat)
    print(f'✅ Flattened file written to: {OUTPUT}')