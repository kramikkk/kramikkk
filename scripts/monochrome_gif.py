#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence


def monochrome_frame(frame: Image.Image) -> Image.Image:
    rgba = frame.convert("RGBA")
    red, green, blue, alpha = rgba.split()
    value = ImageChops.lighter(ImageChops.lighter(red, green), blue)
    lut = [
        max(0, int(channel * 0.65))
        if channel < 35
        else min(255, int(70 + channel * 0.72))
        for channel in range(256)
    ]
    gray = value.point(lut)

    return Image.merge("RGBA", (gray, gray, gray, alpha))


def convert_gif(input_path: Path, output_path: Path) -> None:
    with Image.open(input_path) as source:
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(source):
            frames.append(monochrome_frame(frame))
            durations.append(frame.info.get("duration", source.info.get("duration", 25)))

        first, *rest = frames
        first.save(
            output_path,
            save_all=True,
            append_images=rest,
            duration=durations,
            loop=source.info.get("loop", 0),
            disposal=2,
            optimize=True,
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert an animated GIF to monochrome.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    convert_gif(args.input, args.output)


if __name__ == "__main__":
    main()
