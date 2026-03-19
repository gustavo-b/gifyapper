# GifYapper

Add speech bubbles to GIFs. Includes a browser-based preview for visual positioning.

![milly](https://github.com/user-attachments/assets/a476f3d1-878b-4466-99e5-0016b05913c1)


## Setup

### Nix

```bash
nix develop
gifyapper input.gif
```

### uv

Requires [ImageMagick](https://imagemagick.org/) installed separately:

```bash
# Ubuntu/Debian
sudo apt install imagemagick

# macOS
brew install imagemagick

# Arch
sudo pacman -S imagemagick
```

Then:

```bash
uv venv
source .venv/bin/activate
uv pip install .
gifyapper input.gif
```

## Usage

```bash
# Interactive mode (opens browser preview)
gifyapper input.gif

# Headless mode
gifyapper input.gif --no-preview -o output.gif

# Platform color presets (sets bubble color)
gifyapper input.gif --bg discord
gifyapper input.gif --bg telegram
gifyapper input.gif --bg twitter

# Custom hex color
gifyapper input.gif --bg "#FF6600"

# Bubble shape
gifyapper input.gif --shape circle
gifyapper input.gif --shape box --corner-radius 12

# Tail options
gifyapper input.gif --tail bottom-left --tail-size 40 --tail-angle 60 --tail-tilt 10

# Canvas padding
gifyapper input.gif --pad-top 80 --pad-bottom 40

# Custom dimensions and position (headless)
gifyapper input.gif --no-preview --bubble-width 300 --bubble-height 100 --position 50 20
```
