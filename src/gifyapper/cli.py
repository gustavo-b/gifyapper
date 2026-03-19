from pathlib import Path

import click
from PIL import Image

from gifyapper.bubble import render_bubble
from gifyapper.compositor import composite_gif
from gifyapper.preview import run_preview

BG_PRESETS = {
    "discord": "#323339",
    "telegram": "#17212B",
    "twitter": "#15202B",
    "black": "#000000",
    "white": "#FFFFFF",
}


@click.command()
@click.argument("input_gif", type=click.Path(exists=True))
@click.option("-o", "--output", default=None, help="Output GIF path (default: input_yap.gif)")
@click.option("--bg", default="discord", help="Bubble color preset or hex (discord, telegram, twitter, black, white, or #RRGGBB)")
@click.option("--pad-top", default=0, type=int, help="Pixels to add above the GIF")
@click.option("--pad-bottom", default=0, type=int, help="Pixels to add below the GIF")
@click.option("--shape", default="circle", type=click.Choice(["circle", "box"]), help="Bubble shape")
@click.option("--corner-radius", default=20, type=int, help="Corner radius (box shape only)")
@click.option("--tail", default="bottom-right", type=click.Choice(["bottom-right", "bottom-left", "bottom-center", "top-right", "top-left", "top-center"]))
@click.option("--bubble-width", default=None, type=int, help="Bubble width (default: 60% of GIF width)")
@click.option("--bubble-height", default=80, type=int, help="Bubble height")
@click.option("--tail-position", default=0.65, type=float, help="Tail position along edge (0.0-1.0)")
@click.option("--tail-size", default=30, type=int, help="Tail triangle length")
@click.option("--tail-angle", default=40, type=int, help="Tail width in degrees (wider = fatter)")
@click.option("--no-preview", is_flag=True, help="Skip visual preview, use defaults or --position")
@click.option("--position", nargs=2, type=int, default=None, help="Bubble position as X Y (use with --no-preview)")
def main(input_gif, output, bg, pad_top, pad_bottom,
         shape, corner_radius, tail, bubble_width, bubble_height,
         tail_position, tail_size, tail_angle,
         no_preview, position):
    """Add a speech bubble to a GIF."""
    bubble_color = BG_PRESETS.get(bg, bg)

    if output is None:
        p = Path(input_gif)
        output = str(p.with_name(p.stem + "_yap" + p.suffix))

    gif = Image.open(input_gif)
    gif_w, gif_h = gif.size

    if bubble_width is None:
        bubble_width = int(gif_w * 0.6)

    bubble = render_bubble(
        width=bubble_width,
        height=bubble_height,
        bubble_color=bubble_color,
        shape=shape,
        corner_radius=corner_radius,
        tail_direction=tail,
        tail_position=tail_position,
        tail_size=tail_size,
        tail_angle=tail_angle,
    )

    if no_preview:
        bx, by = position if position else (max(0, (gif_w - bubble.width) // 2), 10)
    else:
        gif.seek(0)
        first_frame = gif.convert("RGBA")
        static_dir = Path(__file__).resolve().parent.parent.parent / "static"

        result = run_preview(first_frame, bubble.width, bubble.height, bubble_color, static_dir)

        bx = result["x"]
        by = result["y"]
        pad_top = result.get("pad_top", pad_top)
        tail = result.get("tail_direction", tail)
        shape = result.get("shape", shape)
        corner_radius = result.get("corner_radius", corner_radius)
        tail_position = result.get("tail_position", tail_position)
        tail_size = result.get("tail_size", tail_size)
        tail_angle = result.get("tail_angle", tail_angle)
        new_width = result.get("width", bubble.width)
        new_height = result.get("height", bubble.height)

        bubble = render_bubble(
            width=new_width,
            height=new_height,
            bubble_color=bubble_color,
            shape=shape,
            corner_radius=corner_radius,
            tail_direction=tail,
            tail_position=tail_position,
            tail_size=tail_size,
            tail_angle=tail_angle,
        )

    composite_gif(
        input_path=input_gif,
        output_path=output,
        bubble_img=bubble,
        bubble_x=bx,
        bubble_y=by,
        pad_top=pad_top,
        pad_bottom=pad_bottom,
        bg_color=bubble_color,
    )

    click.echo(f"Saved to {output}")


if __name__ == "__main__":
    main()
