from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from rich import print
from rich.table import Table
import requests
import os
import sys
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    try:
        result = urlparse(url)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except Exception:
        return False

def get_exif_dict(img: Image.Image) -> Dict:
    """Return EXIF data as a tag-name → value dict."""
    try:
        exif_data = img._getexif()
    except (AttributeError, OSError):
        return {}
    
    if not exif_data:
        return {}
    exif = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        exif[tag] = value
    return exif

def get_gps_info(exif: Dict) -> Optional[Dict]:
    """Extract GPS info from EXIF dict and convert to useful form."""
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    # gps_info keys are numeric; map them to names
    gps_data = {}
    for key, val in gps_info.items():
        name = GPSTAGS.get(key, key)
        gps_data[name] = val

    def _convert_to_degrees(value: Tuple) -> Optional[float]:
        """
        Convert GPS coordinates stored in EXIF to degrees in float.
        'value' is usually a tuple like (IFDRational, IFDRational, IFDRational)
        or ((num, den), (num, den), (num, den)).
        """
        def to_float(r):
            # r might be IFDRational, a tuple (num, den), or already a float/int
            try:
                return float(r)
            except (TypeError, ZeroDivisionError):
                # assume (num, den)
                try:
                    num, den = r
                    if den == 0:
                        return None
                    return num / den
                except (TypeError, ValueError):
                    return None

        d = to_float(value[0])
        m = to_float(value[1])
        s = to_float(value[2])
        
        if d is None or m is None or s is None:
            return None

        return d + (m / 60.0) + (s / 3600.0)

    lat = lon = None

    if "GPSLatitude" in gps_data and "GPSLatitudeRef" in gps_data:
        lat = _convert_to_degrees(gps_data["GPSLatitude"])
        if lat is not None and gps_data["GPSLatitudeRef"] in ["S", b"S"]:
            lat = -lat

    if "GPSLongitude" in gps_data and "GPSLongitudeRef" in gps_data:
        lon = _convert_to_degrees(gps_data["GPSLongitude"])
        if lon is not None and gps_data["GPSLongitudeRef"] in ["W", b"W"]:
            lon = -lon

    gps_data["LatitudeDecimal"] = lat
    gps_data["LongitudeDecimal"] = lon
    return gps_data

def download_image(url: str, filename: str) -> bool:
    """Download an image from URL and save it locally."""
    if not validate_url(url):
        print("[bold red]Invalid URL format.[/bold red]")
        return False
    
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        print(f"[bold green]Saved as {filename}[/bold green]")
        return True
    except requests.exceptions.MissingSchema:
        print("[bold red]Error: Invalid URL (missing schema like http/https)[/bold red]")
        return False
    except requests.exceptions.ConnectionError:
        print("[bold red]Error: Failed to connect to the URL.[/bold red]")
        return False
    except requests.exceptions.Timeout:
        print("[bold red]Error: Request timed out.[/bold red]")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"[bold red]HTTP Error: {e.response.status_code}[/bold red]")
        return False
    except Exception as e:
        print(f"[bold red]Error downloading image: {str(e)}[/bold red]")
        return False

def main():
    """Main execution function."""
    print("[bold purple]Welcome to JPG Info & Metadata Extractor[/bold purple]")
    choice = input("Download an image? (yes/no): ").strip().lower()

    if choice == "yes":
        print("[bold yellow]Enter image URL: [/bold yellow]", end="")
        url = input().strip()
        
        if not url:
            print("[bold red]URL cannot be empty.[/bold red]")
            return
        
        filename = input("Save as filename (without extension): ").strip()
        if not filename:
            print("[bold red]Filename cannot be empty.[/bold red]")
            return
        
        filename += ".jpg"
        
        if not download_image(url, filename):
            return
        
        image_path = filename
    else:
        image_path = input("Enter the path to the JPG image: ").strip()

    # ---- BASIC IMAGE INFO ----
    if not os.path.isfile(image_path):
        print(f"[bold red]File not found:[/bold red] {image_path}")
        return

    try:
        img = Image.open(image_path)
    except IOError:
        print(f"[bold red]Error: Cannot open image file.[/bold red] {image_path}")
        return
    except Exception as e:
        print(f"[bold red]Error opening image: {str(e)}[/bold red]")
        return

    print("\n[bold cyan]Basic Image Info[/bold cyan]")
    print(f"Path        : {image_path}")
    print(f"Format      : {img.format}")
    print(f"Mode        : {img.mode}")
    print(f"Size (WxH)  : {img.size[0]} x {img.size[1]} pixels")
    print(f"File size   : {os.path.getsize(image_path)} bytes")

    if img.format and img.format != "JPEG":
        print("[bold yellow]Warning:[/bold yellow] This script is designed for JPEG. EXIF may be missing.")

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
                print("\n[bold yellow]GPS coordinates could not be converted.[/bold yellow]")
        else:
            print("\n[bold red]No GPS information found.[/bold red]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
        sys.exit(1)