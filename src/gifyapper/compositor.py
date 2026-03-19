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
        ]

        if pad_top > 0 or pad_bottom > 0:
            if pad_top > 0:
                cmd += [
                    "-gravity", "north",
                    "-background", bg_color,
                    "-splice", f"0x{pad_top}",
                ]
            if pad_bottom > 0:
                cmd += [
                    "-gravity", "south",
                    "-background", bg_color,
                    "-splice", f"0x{pad_bottom}",
                ]

        # Composite bubble onto each frame
        cmd += [
            "null:",
            str(bubble_path),
            "-gravity", "northwest",
            "-geometry", f"+{bubble_x}+{bubble_y}",
            "-layers", "Composite",
            str(output_path),
        ]

        subprocess.run(cmd, check=True)
