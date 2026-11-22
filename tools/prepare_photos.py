# prepare_photos.py
# Usage: python prepare_photos.py originals_folder output_folder
import sys
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import subprocess

SRC = Path(sys.argv[1])          # raw photos (the gitignored folder)
DST = Path(sys.argv[2])          # web-ready copies (the folder you commit)
WATERMARK = "Donald Pepka"
FONT_PATH = "assets/photos_raw/OldStandardTT-Regular.ttf"
MAX_SIZE = None                  # None = keep full resolution; or e.g. 2400 to cap the long side
QUALITY = 95                     # JPEG quality (95 is near-lossless; lower = smaller files)

# ---- WHITELIST: the only metadata that survives ----------------------------
# Tags in the main EXIF block ("IFD0")
KEEP_MAIN = {
    0x010F: "Make",              # e.g. Google
    0x0110: "Model",             # e.g. Pixel 8
}
# Tags in the camera-settings block (the "Exif IFD")
KEEP_SETTINGS = {
    0x829A: "ExposureTime",      # shutter speed
    0x829D: "FNumber",           # aperture
    0x8822: "ExposureProgram",
    0x8827: "ISO",
    0x9204: "ExposureBias",
    0x9207: "MeteringMode",
    0x9209: "Flash",
    0x920A: "FocalLength",
    0xA403: "WhiteBalance",
    0xA405: "FocalLengthIn35mm",
    0xA433: "LensMake",
    0xA434: "LensModel",
    # 0x9003: "DateTimeOriginal",   # uncomment to keep the capture date/time
}
# Deliberately NOT kept: GPS, body serial number, owner name, MakerNote,
# embedded thumbnail, XMP, software/editing history.
# -----------------------------------------------------------------------------

DST.mkdir(parents=True, exist_ok=True)

def clean_exif(original):
    """Build a fresh EXIF block containing only whitelisted tags."""
    old = original.getexif()
    old_settings = old.get_ifd(0x8769)         # camera-settings sub-block
    new = Image.Exif()

    for tag in KEEP_MAIN:
        if tag in old:
            new[tag] = old[tag]

    new_settings = new.get_ifd(0x8769)
    for tag in KEEP_SETTINGS:
        if tag in old_settings:
            new_settings[tag] = old_settings[tag]

    return new

for path in sorted(SRC.iterdir()):
    if path.suffix.lower() not in {'.jpg', '.jpeg'}:
        continue

    original = Image.open(path)
    exif = clean_exif(original)                      # read metadata BEFORE any editing
    icc = original.info.get('icc_profile')           # color profile: not private, and keeps colors accurate

    img = ImageOps.exif_transpose(original)          # bake rotation into pixels (orientation tag isn't kept)
    img = img.convert('RGB')
    if MAX_SIZE:
        img.thumbnail((MAX_SIZE, MAX_SIZE))

    # Watermark: semi-transparent text drawn on its own layer, then merged in
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    size = 100
    font = ImageFont.truetype(FONT_PATH, size) if FONT_PATH else ImageFont.load_default(size)
    left, top, right, bottom = draw.textbbox((0, 0), WATERMARK, font=font)
    x = 0
    y = img.height + (top - bottom)
    draw.text((x, y), WATERMARK, font=font, fill=(255, 255, 255, 110))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

    img.save(DST / f'{path.stem}.jpg', quality=QUALITY,
             exif=exif.tobytes(), icc_profile=icc)
    print('wrote', path.stem)

# Now remake the manifest
subprocess.run(
    [sys.executable, str(Path(__file__).parent / 'make_manifest.py'), str(DST)],
    check=True,   # raise an error if the manifest script fails
)
