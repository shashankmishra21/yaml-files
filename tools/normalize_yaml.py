import io
import os

SRC = 'routes/fetch_br.yaml'
DST = 'routes/fetch_br_norm.yaml'

NBSP = '\u00A0'
WSP = '\u2007'
NNBSP = '\u202F'

def normalize(text: str) -> str:
    text = text.replace(NBSP, ' ')
    text = text.replace(WSP, ' ')
    text = text.replace(NNBSP, ' ')
    # Also normalize CRLF to LF and strip trailing spaces
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return '\n'.join([line.rstrip() for line in lines])

with io.open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

norm = normalize(content)

os.makedirs(os.path.dirname(DST), exist_ok=True)
with io.open(DST, 'w', encoding='utf-8') as f:
    f.write(norm)

print(f'✅ Normalized file written to: {DST}')
