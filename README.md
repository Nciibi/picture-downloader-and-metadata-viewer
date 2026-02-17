# Picture Downloader and Metadata Viewer

A Python tool for downloading images and extracting detailed metadata including EXIF data and GPS information.

## Features

- 📥 **Download images** directly from URLs
- 🏷️ **Extract EXIF metadata** from JPEG images
- 🗺️ **Parse GPS coordinates** and convert to decimal format
- 📊 **Display metadata** in a beautifully formatted table
- ✅ **Input validation** and comprehensive error handling
- 🎨 **Rich terminal output** with color-coded information

## Requirements

- Python 3.7+
- PIL (Pillow)
- requests
- rich

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Nciibi/picture-downloader-and-metadata-viewer.git
cd picture-downloader-and-metadata-viewer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install pillow requests rich
```

## Usage

Run the script:
```bash
python metadata.py
```

### Options

1. **Download an image**: The script will prompt you to enter an image URL
   - Enter a valid HTTP/HTTPS URL
   - Provide a filename (without extension, .jpg will be added)
   
2. **Use a local image**: Skip the download and provide the path to an existing JPEG file

### Example

```bash
$ python metadata.py
Welcome to JPG Info & Metadata Extractor
Download an image? (yes/no): yes
Enter image URL: https://example.com/photo.jpg
Save as filename (without extension): my_photo

Saved as my_photo.jpg

Basic Image Info
Path        : my_photo.jpg
Format      : JPEG
Mode        : RGB
Size (WxH)  : 4000 x 3000 pixels
File size   : 2457652 bytes

EXIF Metadata
[Table with metadata tags and values]

GPS Information
[GPS data and decimal coordinates]

Decimal Coordinates: 40.7128, -74.0060
You can paste these in Google Maps.
```

## Output

The tool displays:

- **Basic Image Info**: Format, dimensions, file size
- **EXIF Metadata**: Camera settings, date taken, manufacturer, etc.
- **GPS Information**: GPS coordinates in both DMS (Degrees, Minutes, Seconds) and decimal formats
- **Map Link**: Decimal coordinates ready to paste into Google Maps

## Error Handling

The script includes robust error handling for:
- Invalid URLs
- Network connection failures
- Request timeouts
- Missing or corrupted image files
- Missing EXIF metadata
- Invalid GPS coordinate data
- User interruption (Ctrl+C)

## Functions

### `validate_url(url: str) -> bool`
Validates if a string is a properly formatted URL.

### `get_exif_dict(img: Image.Image) -> Dict`
Extracts EXIF data from an image and returns it as a dictionary.

### `get_gps_info(exif: Dict) -> Optional[Dict]`
Extracts GPS information from EXIF data and converts DMS coordinates to decimal format.

### `download_image(url: str, filename: str) -> bool`
Downloads an image from a URL with error handling.

### `main()`
Main execution function that orchestrates the entire workflow.

## Limitations

- Primarily designed for JPEG images (may work with other formats that support EXIF)
- Requires images to have EXIF metadata embedded for full functionality
- GPS information is only available if the camera had GPS enabled when taking the photo

## License

This project is open source and available on GitHub.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
