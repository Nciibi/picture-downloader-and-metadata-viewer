from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from rich import print
from rich.table import Table
import requests
import os
import sys
import piexif
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

def create_custom_metadata() -> Dict:
    """Allow user to create custom EXIF metadata from scratch."""
    print("\n[bold cyan]Create Custom EXIF Metadata[/bold cyan]")
    print("Enter metadata fields (press Enter to skip):")
    
    custom_exif = {}
    common_tags = [
        "ImageDescription",
        "Make",
        "Model",
        "Software",
        "DateTime",
        "Artist",
        "Copyright",
        "WhitePoint",
        "YCbCrPositioning"
    ]
    
    for tag in common_tags:
        value = input(f"{tag}: ").strip()
        if value:
            custom_exif[tag] = value
    
    # Ask for custom tags
    while True:
        custom_tag = input("\nAdd custom tag name (or press Enter to finish): ").strip()
        if not custom_tag:
            break
        custom_value = input(f"Value for '{custom_tag}': ").strip()
        if custom_value:
            custom_exif[custom_tag] = custom_value
    
    if custom_exif:
        print(f"\n[bold green]Created {len(custom_exif)} custom metadata fields.[/bold green]")
    
    return custom_exif

def display_custom_metadata(metadata: Dict):
    """Display custom metadata in a formatted table."""
    if not metadata:
        print("[bold yellow]No custom metadata to display.[/bold yellow]")
        return
    
    print("\n[bold cyan]Custom Metadata[/bold cyan]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Field", style="bold")
    table.add_column("Value", overflow="fold")
    
    for key, value in metadata.items():
        table.add_row(str(key), str(value))
    
    print(table)

def modify_metadata(image_path: str, exif: Dict) -> bool:
    """Allow user to modify EXIF metadata and save to image."""
    while True:
        print("\n[bold cyan]Metadata Modification Menu[/bold cyan]")
        print("Choose an option:")
        print("1. Modify existing EXIF tag")
        print("2. Remove GPS data")
        print("3. Strip all EXIF data")
        print("4. Save modified image")
        print("5. Exit without saving")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            tag = input("Enter tag name to modify: ").strip()
            if tag not in exif:
                print(f"[bold yellow]Tag '{tag}' not found in EXIF data.[/bold yellow]")
                continue
            
            new_value = input(f"Enter new value for '{tag}': ").strip()
            exif[tag] = new_value
            print(f"[bold green]Updated '{tag}' to '{new_value}'[/bold green]")
        
        elif choice == "2":
            if "GPSInfo" in exif:
                del exif["GPSInfo"]
                print("[bold green]GPS data removed.[/bold green]")
            else:
                print("[bold yellow]No GPS data found to remove.[/bold yellow]")
        
        elif choice == "3":
            confirm = input("Are you sure you want to strip all EXIF data? (yes/no): ").strip().lower()
            if confirm == "yes":
                exif.clear()
                print("[bold green]All EXIF data cleared.[/bold green]")
        
        elif choice == "4":
            save_exif_to_image(image_path, exif)
            return True
        
        elif choice == "5":
            print("[bold yellow]Exiting without saving.[/bold yellow]")
            return False
        
        else:
            print("[bold red]Invalid choice. Please try again.[/bold red]")

def save_exif_to_image(image_path: str, exif: Dict) -> bool:
    """Save modified EXIF data back to the image."""
    try:
        # Open and convert image if needed
        img = Image.open(image_path)
        
        # Convert palette/grayscale images to RGB for JPEG
        if img.mode in ('P', 'L', 'LA', 'PA'):
            img = img.convert('RGB')
        
        # Create output path
        if ".jpg" in image_path.lower():
            output_path = image_path.replace(".jpg", "_modified.jpg").replace(".JPG", "_modified.jpg")
        else:
            output_path = image_path + "_modified.jpg"
        
        # Try to save with piexif format
        try:
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}}
            
            for tag, value in exif.items():
                if tag == "GPSInfo":
                    continue
                
                # Find the tag ID
                tag_id = None
                for tid, tname in TAGS.items():
                    if tname == tag:
                        tag_id = tid
                        break
                
                # Only add tags that piexif can handle
                if tag_id and tag_id not in [0x0100, 0x0101, 0x0102, 0x0103, 0x0106, 0x0111, 0x0115, 0x0116, 0x0117]:
                    try:
                        # Convert value to proper format for piexif
                        val = str(value).encode('utf-8') if isinstance(value, str) else value
                        exif_dict["0th"][tag_id] = val
                    except Exception:
                        pass
            
            exif_bytes = piexif.dump(exif_dict)
            img.save(output_path, "jpeg", exif=exif_bytes)
        except Exception as e:
            # Fallback: save without EXIF if piexif fails
            print(f"[bold yellow]Warning: Could not save with EXIF metadata: {str(e)}[/bold yellow]")
            img.save(output_path, "jpeg")
        
        print(f"[bold green]Modified image saved as: {output_path}[/bold green]")
        return True
    
    except Exception as e:
        print(f"[bold red]Error saving image: {str(e)}[/bold red]")
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
        create_choice = input("Would you like to create custom metadata? (yes/no): ").strip().lower()
        if create_choice == "yes":
            exif = create_custom_metadata()
            display_custom_metadata(exif)
            # Ask to save custom metadata
            save_choice = input("\nSave custom metadata to image? (yes/no): ").strip().lower()
            if save_choice == "yes":
                save_exif_to_image(image_path, exif)
    
    if exif:
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

        # ---- MODIFY METADATA ----
        modify_choice = input("\nWould you like to modify the metadata? (yes/no): ").strip().lower()
        if modify_choice == "yes":
            modify_metadata(image_path, exif)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[bold yellow]Operation cancelled by user.[/bold yellow]")
        sys.exit(0)
    except Exception as e:
        print(f"\n[bold red]Unexpected error: {str(e)}[/bold red]")
        sys.exit(1)