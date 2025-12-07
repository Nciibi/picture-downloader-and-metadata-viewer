from PIL import Image
from PIL.ExifTags import TAGS
import requests
from rich import print
print
print("[bold purple]Welcome to Metadata Extractor[/bold purple]")
print("download an image or use your own to extract metadata (yes => download , no => use your own image)", end="")
choice = input().strip().lower()
if choice == 'yes':
    print("[bold yellow]url of the picture   : [/bold yellow]",end="") # paste the URL here
    url=input().strip()
    filename = input("Enter the filename to save the image : ")+".jpg"

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, stream=True)
    response.raise_for_status()  # will raise an error if download failed
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive chunks
                f.write(chunk)

    print(f"[bold green ]Saved as {filename}[/bold green]")
    image_path = filename

if choice == 'no':
    image_path = input("Enter the path to the image file (if in the same file path should start with './'): ")





# Open the image
img = Image.open(image_path)

# Get EXIF data
exif_data = img._getexif()

if not exif_data:
    print("No EXIF metadata found.")
else:
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        print(f"{tag}: {value}")