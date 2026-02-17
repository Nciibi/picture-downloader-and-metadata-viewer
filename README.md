# Picture Downloader and Metadata Viewer

A powerful Python tool for downloading images, extracting detailed metadata including EXIF data and GPS information, and modifying or creating custom metadata.

## Features

- 📥 **Download images** directly from URLs with validation and error handling
- 🏷️ **Extract EXIF metadata** from JPEG images comprehensively
- 🗺️ **Parse GPS coordinates** and convert from DMS to decimal format
- 📊 **Display metadata** in beautifully formatted tables using Rich library
- ✏️ **Modify metadata** - Edit, remove, or strip EXIF data interactively
- ➕ **Create custom metadata** - Add your own metadata tags when none exist
- 🖼️ **Image format handling** - Automatically converts incompatible image modes to JPEG-compatible formats
- ✅ **Robust error handling** - Network errors, file issues, and corrupted data handled gracefully
- 🎨 **Rich terminal output** - Color-coded information with beautiful formatting

## Requirements

- Python 3.7+
- PIL (Pillow)
- requests
- rich
- piexif

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

## Workflow

1. **Download or load image** - Choose to download from URL or load a local file
2. **View metadata** - See EXIF and GPS information in formatted tables
   - If no EXIF exists, option to create custom metadata
3. **Modify metadata** (optional) - Edit individual tags, remove GPS data, or strip all EXIF
4. **Save modified image** - Save the modified image with updated metadata as `*_modified.jpg`

## Modification Options

When modifying metadata, you can:
- **Modify existing tags**: Update any EXIF tag value
- **Remove GPS data**: Strip GPS coordinates while keeping other metadata
- **Strip all EXIF**: Remove all metadata from the image
- **Save**: Write changes to a new file with `_modified.jpg` suffix
- **Exit without saving**: Discard all changes

## Creating Custom Metadata

If an image has no EXIF data, you can create custom metadata including:
- Common fields: Make, Model, DateTime, Artist, Copyright, Software, etc.
- Custom tag names and values
- Save the metadata directly to the image

### Example Workflow

```bash
$ python metadata.py
Welcome to JPG Info & Metadata Extractor
Download an image? (yes/no): no
Enter the path to the JPG image: photo.jpg

Basic Image Info
Path        : photo.jpg
Format      : JPEG
Mode        : RGB
Size (WxH)  : 4000 x 3000 pixels
File size   : 2457652 bytes

EXIF Metadata
[Table with metadata]

Would you like to modify the metadata? (yes/no): yes

Metadata Modification Menu
Choose an option:
1. Modify existing EXIF tag
2. Remove GPS data
3. Strip all EXIF data
4. Save modified image
5. Exit without saving

Enter your choice (1-5): 1
Enter tag name to modify: Artist
Enter new value for 'Artist': John Doe
Updated 'Artist' to 'John Doe'

[Menu repeats or continue with more modifications]

Enter your choice (1-5): 4
Modified image saved as: photo_modified.jpg
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
Validates if a string is a properly formatted URL with http/https schema.

### `get_exif_dict(img: Image.Image) -> Dict`
Extracts EXIF data from an image and returns it as a dictionary with tag names as keys.

### `get_gps_info(exif: Dict) -> Optional[Dict]`
Extracts GPS information from EXIF data and converts DMS coordinates to decimal format.
Handles edge cases like zero denominators and invalid coordinate data.

### `download_image(url: str, filename: str) -> bool`
Downloads an image from a URL with comprehensive error handling for network issues, timeouts, and HTTP errors.

### `create_custom_metadata() -> Dict`
Interactive function allowing users to create custom EXIF metadata from scratch with common fields and custom tags.

### `display_custom_metadata(metadata: Dict)`
Displays custom metadata in a formatted Rich table.

### `modify_metadata(image_path: str, exif: Dict) -> bool`
Interactive menu for modifying EXIF metadata with options to edit tags, remove GPS, strip all data, or save changes.
Loops to allow multiple modifications before saving.

### `save_exif_to_image(image_path: str, exif: Dict) -> bool`
Saves modified EXIF data back to the image file as `*_modified.jpg`.
Automatically converts incompatible image modes (palette, grayscale) to RGB for JPEG compatibility.
Includes fallback to save without EXIF if piexif encoding fails.

### `main()`
Main execution function that orchestrates the entire workflow from user input to metadata display and modification.

## Error Handling

The script includes robust error handling for:
- **Network issues**: Connection failures, timeouts, HTTP errors
- **File operations**: Missing files, corrupted image files, permission errors
- **EXIF operations**: Invalid or missing EXIF data, GPS coordinate conversion errors
- **Image format issues**: Palette/grayscale images automatically converted to RGB
- **User input**: Invalid URLs, empty filenames, non-existent tags
- **Keyboard interrupts**: Graceful exit on Ctrl+C

## Limitations

- Primarily designed for JPEG images (works with other formats but EXIF support varies)
- Requires images to have EXIF metadata embedded for full functionality (can create custom)
- GPS information only available if camera had GPS enabled when photo was taken
- Some EXIF tags are read-only and cannot be modified through piexif

## Improvements Made

- **Type hints** throughout for better code documentation
- **Comprehensive error handling** for network, file, and image issues
- **Input validation** with URL and filename checks
- **GPS coordinate validation** preventing division by zero errors
- **Image mode handling** - Converts incompatible formats to JPEG-compatible RGB
- **Graceful degradation** - Falls back to saving without EXIF if encoding fails
- **Interactive modification menu** with looping for multiple edits
- **Custom metadata creation** when EXIF data doesn't exist

## Future Enhancements

Possible additions for future versions:
- Support for more image formats (PNG with EXIF, WebP, TIFF)
- IPTC and XMP metadata support
- Batch processing multiple images
- GUI interface using tkinter or web framework
- Metadata comparison between images
- Template-based metadata application

## License

This project is open source and available on GitHub.

## Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
