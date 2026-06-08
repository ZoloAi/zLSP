"""
generate_icon_tints.py — produce per-role .zolo file icons from the base mark.

The base icon (zolo_filetype.png) is green. Each zOS file role gets a hue-shifted
variant whose color matches the canonical bifrost palette (zbifrost-client
zbase.css). Recolor method: convert to HSV, SET hue to the target (keep S+V) but
only on saturated pixels — so the white "Z", the ".zolo" pill, and the sparkles
stay white while the colored body + lightning take the brand hue. V is preserved,
so the gradient/shading survives.

zSpark and any other .zolo keep the green base (handled by the base `zolo`
language), so no variant is generated for them.

Usage:
    python3 -m zlsp.assets.generate_icon_tints
"""
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image

# role -> canonical hex (SSOT: zbifrost-client/zSys/theme/zbase.css)
ROLE_COLORS = {
    'ui': '#9370DB',      # SECONDARY — purple
    'env': '#5CA9FF',     # INFO — blue
    'server': '#E63946',  # DANGER — red
    'raven': '#FFB347',   # WARNING — amber
}

# Pixels below this saturation (0-255) are treated as "white/neutral" and left
# untouched (the Z, the pill, sparkles, highlights).
_SAT_THRESHOLD = 40


def _target_hue_255(hex_color: str) -> int:
    h = hex_color.lstrip('#')
    r, g, b = (int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))
    hue, _, _ = colorsys.rgb_to_hsv(r, g, b)
    return int(round(hue * 255))


def tint(src: Image.Image, hex_color: str) -> Image.Image:
    alpha = src.split()[3]
    hsv = np.array(src.convert('RGB').convert('HSV'))
    sat = hsv[..., 1]
    mask = sat > _SAT_THRESHOLD
    hsv[..., 0][mask] = _target_hue_255(hex_color)
    out = Image.fromarray(hsv, 'HSV').convert('RGB')
    out.putalpha(alpha)
    return out


def main() -> int:
    assets = Path(__file__).parent
    base_path = assets / 'zolo_filetype.png'
    base = Image.open(base_path).convert('RGBA')
    for role, hex_color in ROLE_COLORS.items():
        dest = assets / f'zolo_filetype.{role}.png'
        tint(base, hex_color).save(dest)
        print(f'  - {dest.name}  ({hex_color})')
    print(f'Done — {len(ROLE_COLORS)} tinted icons in {assets}/')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
