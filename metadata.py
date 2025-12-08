from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from rich import print
from rich.table import Table
import requests
import os

def get_exif_dict(img):
    """Return EXIF data as a tag-name → value dict."""
    exif_data = img._getexif()
    if not exif_data:
        return {}
    exif = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value
    return exif

def get_gps_info(exif):
    """Extract GPS info from EXIF dict and convert to useful form."""
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    # gps_info keys are numeric; map them to names
    gps_data = {}
    for key, val in gps_info.items():
        name = GPSTAGS.get(key, key)
        gps_data[name] = val

    def _convert_to_degrees(value):
        """
        Convert GPS coordinates stored in EXIF to degrees in float.
        'value' is usually a tuple like (IFDRational, IFDRational, IFDRational)
        or ((num, den), (num, den), (num, den)).
        """
        def to_float(r):
            # r might be IFDRational, a tuple (num, den), or already a float/int
            try:
                return float(r)
            except TypeError:
                # assume (num, den)
                num, den = r
                return num / den

        d = to_float(value[0])
        m = to_float(value[1])
        s = to_float(value[2])

        return d + (m / 60.0) + (s / 3600.0)

    lat = lon = None

    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        lat = _convert_to_degrees(gps_data["GPSLatitude"])
        if gps_data["GPSLatitudeRef"] in ["S", b"S"]:
            lat = -lat

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        lon = _convert_to_degrees(gps_data["GPSLongitude"])
        if gps_data["GPSLongitudeRef"] in ["W", b"W"]:
            lon = -lon

    gps_data["LatitudeDecimal"] = lat
    gps_data["LongitudeDecimal"] = lon
    return gps_data

print("[bold purple]Welcome to JPG Info & Metadata Extractor[/bold purple]")
choice = input("Download an image? (yes/no): ").strip().lower()

if choice == "yes":
    print("[bold yellow]Enter image URL: [/bold yellow]", end="")
    url = input().strip()
    filename = input("Save as filename (without extension): ").strip() + ".jpg"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()

    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    print(f"[bold green]Saved as {filename}[/bold green]")
    image_path = filename
else:
    image_path = input("Enter the path to the JPG image: ").strip()

# ---- BASIC IMAGE INFO ----
if not os.path.isfile(image_path):
    print(f"[bold red]File not found:[/bold red] {image_path}")
    raise SystemExit(1)

img = Image.open(image_path)

print("\n[bold cyan]Basic Image Info[/bold cyan]")
print(f"Path        : {image_path}")
print(f"Format      : {img.format}")
print(f"Mode        : {img.mode}")
print(f"Size (WxH)  : {img.size[0]} x {img.size[1]} pixels")
print(f"File size   : {os.path.getsize(image_path)} bytes")

if img.format != "JPEG":
    print("[bold red]Warning:[/bold red] This script is designed for JPEG. EXIF may be missing.")

# ---- EXIF METADATA ----
exif = get_exif_dict(img)

if not exif:
    print("\n[bold red]No EXIF metadata found.[/bold red]")
else:
    print("\n[bold cyan]EXIF Metadata[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Tag", style="bold")
    table.add_column("Value", overflow="fold")

    for tag, value in exif.items():
        # GPSInfo will be handled separately
        if tag == "GPSInfo":
            continue
        table.add_row(str(tag), str(value))

    print(table)

    # ---- GPS INFO ----
    gps_data = get_gps_info(exif)
    if gps_data:
        print("\n[bold cyan]GPS Information[/bold cyan]")

        gps_table = Table(show_header=True, header_style="bold magenta")
        gps_table.add_column("Field", style="bold")
        gps_table.add_column("Value", overflow="fold")

        for key, value in gps_data.items():
            gps_table.add_row(str(key), str(value))

        print(gps_table)

        lat = gps_data.get("LatitudeDecimal")
        lon = gps_data.get("LongitudeDecimal")
        if lat is not None and lon is not None:
            print(f"\n[bold green]Decimal Coordinates:[/bold green] {lat}, {lon}")
            print("[bold yellow]You can paste these in Google Maps.[/bold yellow]")
    else:
        print("\n[bold red]No GPS information found.[/bold red]")