import subprocess
import tempfile
from pathlib import Path


def composite_gif(
    input_path,
    output_path,
    bubble_img,
    bubble_x=0,
    bubble_y=0,
    pad_top=0,
    pad_bottom=0,
    bg_color="#323339",
):
    """Composite a speech bubble onto every frame of a GIF using ImageMagick."""
    with tempfile.TemporaryDirectory() as tmp:
        bubble_path = Path(tmp) / "bubble.png"
        bubble_img.save(str(bubble_path), format="PNG")

        cmd = [
            "magick", str(input_path),
            "-coalesce",
            "-alpha", "set",
        ]

        pad_bg = "none" if bg_color == "transparent" else bg_color
        if pad_top > 0:
            cmd += [
                "-gravity", "north",
                "-background", pad_bg,
                "-splice", f"0x{pad_top}",
            ]
        elif pad_top < 0:
            cmd += [
                "-gravity", "north",
                "-chop", f"0x{-pad_top}",
            ]
        if pad_bottom > 0:
            cmd += [
                "-gravity", "south",
                "-background", pad_bg,
                "-splice", f"0x{pad_bottom}",
            ]
        elif pad_bottom < 0:
            cmd += [
                "-gravity", "south",
                "-chop", f"0x{-pad_bottom}",
            ]

        # Composite bubble onto each frame
        geo_x = f"+{bubble_x}" if bubble_x >= 0 else str(bubble_x)
        geo_y = f"+{bubble_y}" if bubble_y >= 0 else str(bubble_y)

        composite_args = [
            "null:",
            str(bubble_path),
            "-gravity", "northwest",
            "-geometry", f"{geo_x}{geo_y}",
        ]

        if bg_color == "transparent":
            composite_args += ["-compose", "DstOut"]

        cmd += composite_args + ["-layers", "Composite"]

        if bg_color == "transparent":
            cmd += ["-dispose", "Background"]

        cmd.append(str(output_path))

        subprocess.run(cmd, check=True)
