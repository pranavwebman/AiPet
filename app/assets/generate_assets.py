"""Script to generate high quality SVG/PNG pet frame assets and app icon."""

import os
from pathlib import Path
from PIL import Image, ImageDraw

ASSETS_DIR = Path(__file__).resolve().parent
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Define color palette for cute robot/pet character
BODY_COLOR = "#4A90E2"       # Tech blue
BODY_LIGHT = "#73B2FF"
FACEMASK_COLOR = "#1A202C"   # Dark visor
EYE_COLOR_NORMAL = "#00FFC8" # Bright cyan glowing eyes
EYE_COLOR_HAPPY = "#FFD166"  # Warm yellow
EYE_COLOR_THINKING = "#A06CD5" # Purple glow
EYE_COLOR_ERROR = "#EF476F"   # Soft red
EYE_COLOR_SLEEP = "#4A5568"   # Closed dim eyes

FRAMES = {
    "idle": {"eye": EYE_COLOR_NORMAL, "expression": "normal", "mouth": "smile"},
    "hover": {"eye": EYE_COLOR_NORMAL, "expression": "wide", "mouth": "open_smile"},
    "clicked": {"eye": EYE_COLOR_HAPPY, "expression": "happy", "mouth": "open_smile"},
    "thinking": {"eye": EYE_COLOR_THINKING, "expression": "thinking", "mouth": "dots"},
    "talking": {"eye": EYE_COLOR_NORMAL, "expression": "normal", "mouth": "talking"},
    "happy": {"eye": EYE_COLOR_HAPPY, "expression": "happy", "mouth": "wide_smile"},
    "confused": {"eye": EYE_COLOR_THINKING, "expression": "confused", "mouth": "wavy"},
    "error": {"eye": EYE_COLOR_ERROR, "expression": "error", "mouth": "sad"},
    "sleeping": {"eye": EYE_COLOR_SLEEP, "expression": "sleeping", "mouth": "sleeping"},
}

def draw_pet(state: str, size: int = 128) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    spec = FRAMES.get(state, FRAMES["idle"])
    eye_col = spec["eye"]
    expr = spec["expression"]
    mouth = spec["mouth"]

    # Outer ears / antenna
    draw.ellipse([size * 0.15, size * 0.1, size * 0.3, size * 0.25], fill=BODY_LIGHT)
    draw.ellipse([size * 0.7, size * 0.1, size * 0.85, size * 0.25], fill=BODY_LIGHT)

    # Main head body (rounded rectangle)
    margin = size * 0.15
    draw.rounded_rectangle(
        [margin, size * 0.2, size - margin, size * 0.85],
        radius=int(size * 0.25),
        fill=BODY_COLOR,
        outline=BODY_LIGHT,
        width=int(size * 0.03)
    )

    # Dark Visor / Screen Face
    v_left = size * 0.22
    v_top = size * 0.32
    v_right = size * 0.78
    v_bottom = size * 0.72
    draw.rounded_rectangle(
        [v_left, v_top, v_right, v_bottom],
        radius=int(size * 0.15),
        fill=FACEMASK_COLOR
    )

    # Eyes drawing logic
    left_eye_center = (size * 0.38, size * 0.48)
    right_eye_center = (size * 0.62, size * 0.48)
    eye_radius = size * 0.07

    if expr == "sleeping":
        # Arc for closed eyes
        draw.arc([left_eye_center[0]-eye_radius, left_eye_center[1]-eye_radius,
                  left_eye_center[0]+eye_radius, left_eye_center[1]+eye_radius],
                 start=0, end=180, fill=eye_col, width=int(size*0.03))
        draw.arc([right_eye_center[0]-eye_radius, right_eye_center[1]-eye_radius,
                  right_eye_center[0]+eye_radius, right_eye_center[1]+eye_radius],
                 start=0, end=180, fill=eye_col, width=int(size*0.03))
    elif expr == "happy":
        # Crescent happy eyes ^ ^
        draw.arc([left_eye_center[0]-eye_radius, left_eye_center[1]-eye_radius/2,
                  left_eye_center[0]+eye_radius, left_eye_center[1]+eye_radius*1.2],
                 start=180, end=360, fill=eye_col, width=int(size*0.04))
        draw.arc([right_eye_center[0]-eye_radius, right_eye_center[1]-eye_radius/2,
                  right_eye_center[0]+eye_radius, right_eye_center[1]+eye_radius*1.2],
                 start=180, end=360, fill=eye_col, width=int(size*0.04))
    elif expr == "error":
        # X X eyes
        r = eye_radius
        for (cx, cy) in [left_eye_center, right_eye_center]:
            draw.line([cx-r, cy-r, cx+r, cy+r], fill=eye_col, width=int(size*0.04))
            draw.line([cx-r, cy+r, cx+r, cy-r], fill=eye_col, width=int(size*0.04))
    else:
        # Standard glowing circle eyes
        draw.ellipse([left_eye_center[0]-eye_radius, left_eye_center[1]-eye_radius,
                      left_eye_center[0]+eye_radius, left_eye_center[1]+eye_radius], fill=eye_col)
        draw.ellipse([right_eye_center[0]-eye_radius, right_eye_center[1]-eye_radius,
                      right_eye_center[0]+eye_radius, right_eye_center[1]+eye_radius], fill=eye_col)

    # Mouth drawing logic
    m_center_x = size * 0.5
    m_y = size * 0.62
    m_w = size * 0.12

    if mouth in ("smile", "open_smile", "wide_smile"):
        draw.arc([m_center_x - m_w, m_y - m_w/2, m_center_x + m_w, m_y + m_w/2],
                 start=0, end=180, fill=eye_col, width=int(size*0.03))
    elif mouth == "talking":
        draw.ellipse([m_center_x - m_w/2, m_y - m_w/3, m_center_x + m_w/2, m_y + m_w/3], fill=eye_col)
    elif mouth == "sad":
        draw.arc([m_center_x - m_w, m_y, m_center_x + m_w, m_y + m_w],
                 start=180, end=360, fill=eye_col, width=int(size*0.03))
    else:
        draw.line([m_center_x - m_w/2, m_y, m_center_x + m_w/2, m_y], fill=eye_col, width=int(size*0.03))

    return img

def main():
    for state in FRAMES.keys():
        img = draw_pet(state, size=256)
        out_path = ASSETS_DIR / f"pet_{state}.png"
        img.save(out_path, "PNG")
        print(f"Generated asset: {out_path}")

    # Generate app icon
    icon_img = draw_pet("happy", size=256)
    icon_png = ASSETS_DIR / "icon.png"
    icon_img.save(icon_png, "PNG")

    icon_ico = ASSETS_DIR / "icon.ico"
    icon_img.save(icon_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"Generated icons: {icon_png}, {icon_ico}")

if __name__ == "__main__":
    main()
