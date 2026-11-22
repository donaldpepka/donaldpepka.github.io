import json
import sys
from pathlib import Path
from PIL import Image

# File types that count as images. Anything else in the folder is ignored.
EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}

def read_camera(path):
    """Return a string like 'Google Pixel 8' from the image's EXIF, or ''."""
    try:
        exif = Image.open(path).getexif()
    except Exception:
        return ''
    make = str(exif.get(0x010F, '')).strip()    # e.g. "Google"
    model = str(exif.get(0x0110, '')).strip()   # e.g. "Pixel 9a"
    # Some cameras repeat the brand in the model ("Canon EOS R5"); avoid "Canon Canon EOS R5"
    if make and model.lower().startswith(make.lower()):
        make = ''
    return f'{make} {model}'.strip()

# sys.argv[1:] is every folder you typed after the script name,
# so you can run it on several galleries at once.
for folder in sys.argv[1:]:
    folder = Path(folder)
    manifest = folder / 'manifest.json'

    # If a manifest already exists, load it so we can keep any alt text
    # (and any custom ordering) you've already written.
    old = {}
    if manifest.exists():
        old = {item['file']: item for item in json.loads(manifest.read_text())}

    # List the image files in the folder, sorted by filename.
    # .lower() makes the extension check case-insensitive (.JPG works too).
    names = sorted(f.name for f in folder.iterdir() if f.suffix.lower() in EXTENSIONS)

    # For each file: reuse its old entry if there is one, otherwise make a new
    # entry with blank alt text for you to fill in later.
    items = []
    for name in names:
        item = old.get(name, {'file': name, 'alt': '', 'caption': ''})
        # Only fill in the camera if the entry doesn't have one yet,
        # so anything you edit by hand is never overwritten.
        if 'camera' not in item or item['camera'] == "":
            item['camera'] = read_camera(folder / name)
        items.append(item)

    # Write the result back out as readable (indented) JSON.
    manifest.write_text(json.dumps(items, indent=2))
    print(f'{folder}: {len(items)} images')