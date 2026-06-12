"""Generate PNG PWA icons from SVG (requires: pip install cairosvg pillow). Falls back to copying SVG-only note."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "frontend" / "public"
SVG = PUBLIC / "icons" / "icon.svg"


def main():
    try:
        import cairosvg
        from PIL import Image
        import io

        for size in (192, 512):
            png_bytes = cairosvg.svg2png(url=str(SVG), output_width=size, output_height=size)
            out = PUBLIC / f"pwa-{size}x{size}.png"
            out.write_bytes(png_bytes)
            print(f"Wrote {out}")
        # Apple touch icon
        apple = PUBLIC / "apple-touch-icon.png"
        apple.write_bytes(cairosvg.svg2png(url=str(SVG), output_width=180, output_height=180))
        print(f"Wrote {apple}")
    except ImportError:
        print("Install cairosvg and pillow to generate PNG icons: pip install cairosvg pillow")
        print("PWA will use SVG icon fallback.")


if __name__ == "__main__":
    main()
