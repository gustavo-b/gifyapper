import math

from PIL import Image, ImageDraw

SUPERSAMPLE = 4


def _ellipse_y_bottom(cx, cy, rx, ry, x):
    dx = x - cx
    if abs(dx) >= rx:
        return cy
    return cy + ry * math.sqrt(1 - (dx / rx) ** 2)


def _ellipse_y_top(cx, cy, rx, ry, x):
    dx = x - cx
    if abs(dx) >= rx:
        return cy
    return cy - ry * math.sqrt(1 - (dx / rx) ** 2)


def render_bubble(
    width=200,
    height=80,
    bubble_color="#FFFFFF",
    shape="circle",
    corner_radius=20,
    tail_direction="bottom-right",
    tail_position=0.65,
    tail_size=30,
    tail_angle=40,
):
    """Render a speech bubble as an RGBA PIL Image.

    Renders at 4x resolution and downscales for smooth antialiasing.
    """
    s = SUPERSAMPLE
    bw = width * s
    bh = height * s
    ts = tail_size * s
    cr = corner_radius * s

    tail_base = int(2 * ts * (tail_angle / 90))
    half_base = max(s, tail_base // 2)

    is_bottom = tail_direction.startswith("bottom")
    bubble_y_off = 0 if is_bottom else ts
    img_h = bh + ts

    img = Image.new("RGBA", (bw, img_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    body_rect = [0, bubble_y_off, bw - 1, bubble_y_off + bh - 1]
    if shape == "circle":
        draw.ellipse(body_rect, fill=bubble_color)
    else:
        draw.rounded_rectangle(body_rect, radius=cr, fill=bubble_color)

    cx_pos = int(bw * tail_position)
    cx_pos = max(half_base, min(bw - half_base, cx_pos))
    overlap = 4 * s

    if shape == "circle":
        ecx = bw / 2
        ecy = bubble_y_off + bh / 2
        erx = bw / 2
        ery = bh / 2
        if is_bottom:
            edge_y = _ellipse_y_bottom(ecx, ecy, erx, ery, cx_pos)
            left_y = _ellipse_y_bottom(ecx, ecy, erx, ery, cx_pos - half_base) - overlap
            right_y = _ellipse_y_bottom(ecx, ecy, erx, ery, cx_pos + half_base) - overlap
        else:
            edge_y = _ellipse_y_top(ecx, ecy, erx, ery, cx_pos)
            left_y = _ellipse_y_top(ecx, ecy, erx, ery, cx_pos - half_base) + overlap
            right_y = _ellipse_y_top(ecx, ecy, erx, ery, cx_pos + half_base) + overlap
    else:
        if is_bottom:
            edge_y = bubble_y_off + bh - 1
        else:
            edge_y = bubble_y_off
        left_y = edge_y + (-overlap if is_bottom else overlap)
        right_y = left_y

    if tail_direction == "bottom-right":
        tip = (cx_pos + ts, edge_y + ts)
    elif tail_direction == "bottom-left":
        tip = (cx_pos - ts, edge_y + ts)
    elif tail_direction == "bottom-center":
        tip = (cx_pos, edge_y + ts)
    elif tail_direction == "top-right":
        tip = (cx_pos + ts, edge_y - ts)
    elif tail_direction == "top-left":
        tip = (cx_pos - ts, edge_y - ts)
    elif tail_direction == "top-center":
        tip = (cx_pos, edge_y - ts)
    else:
        tip = (cx_pos + ts, edge_y + ts)

    draw.polygon(
        [(cx_pos - half_base, left_y), tip, (cx_pos + half_base, right_y)],
        fill=bubble_color,
    )

    # Downscale with high-quality resampling for smooth edges
    final = img.resize((width, height + tail_size), Image.Resampling.LANCZOS)
    return final
