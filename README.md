# massive-image-converter
Python code using Pillow to convert images to other formats

```
FORMATS_SUPPORTED = [
    "ALL",        # Will choose all formats below
    "JPEG",       # Joint Photographic Experts Group (JPEG/JPG)
    "PNG",        # Portable Network Graphics
    "GIF",        # Graphics Interchange Format
    "PDF",        # Portable Document Format
    "TIFF",       # Tagged Image img Format
    "WEBP",       # WebP Image Format
    "AVIF",
    "JPEG2000",   # JPEG 2000 (JP2, J2K, JPC, JPF, JPG2)
    "BMP",        # Bitmap
    "ICO",        # Icon Format
    "PCX",        # PCX Image Format
    "EPS",        # Encapsulated PostScript
    "BLP",        # Blizzard Mipmap Format, used in World of Warcraft
    "DDS",        # DirectDraw Surface
    "ICNS",       # Macos icons format
    "DIB",        # Device Independent Bitmap
    "PPM",        # Portable Pixmap (PGM, PBM, PNM)
    "XBM",        # X11 Bitmap
    "PALM",       # Palm Pixmap Format (used on Palm OS devices)
    "IM",         # ImageMagick format
    "SGI",        # Silicon Graphics Image (RGB, RGBA, BW)
    "SPIDER",     # SPIDER Image Format
    "TGA",        # Truevision Targa Image
    "MSP",        # MSP Image Format
]

``` 

# Install

tested with

```
python --version
Python 3.11.8
```

Requires Questionary and Pillow libraries installed:
```
pip install -r requirements.txt
```

# UI USage

Run the script `image_converter.py`
```
python image_converter.py
```

## Setup choices

The first question asks how you want to organize your converted images  
- By image: Creates a directory per image and places all the desired converted formats in it
- By format: Creates a directory per format and places each converted image in the corresponding format inside
```
? How do you want your directories organization ?  (Use arrow keys)
 » By image
   By format
```

Select in what formats you want to convert your images  
⚠️ Selecting "All" will convert each images to 19 formats

```
? Select the formats  (Use arrow keys to move, <space> to select, <a> to toggle, <i> to invert)
 » ○ All
   ○ JPEG
   ○ PNG
   ○ GIF
   ○ PDF
   ○ TIFF
   ....
```

Confirm your choices, select no to go back
```
 Confirm choices ? (Use arrow keys)
 » yes
   no
```

- You can select a whole directory, and it will convert all the images in it
- You can select files one by one, using CTRL+click to select multiple files in the same directory
```
? How to select files (Use arrow keys)
 » Selecting file by file
   A whole directory
```

A window will open. Select the desired files or directory.

# CLI USage

Each arguments can be called separately, skipping corresponding UI question
`--convert_path` argument is a dependency to `--source_files` or/and `--source_dir`

### Available Options

- `--organization`, `-o`  
  Defines how converted files are organized.  
  - `img` → Organizes files by image.  
  - `format` → Organizes files by format.  

- `--convert_to`, `-f`  
  Defines the output formats.  
  - Possible values: `JPEG`, `PNG`, `GIF`, `WEBP`, `AVIF`, `ALL`, etc. (Check `--help`)  

- `--source_files`, `-s`  
  Specifies one or more source files to convert. (space-separated)  
  Needs `--convert_path`

- `--source_dir`, `-d`  
  Specifies a directory containing the files to convert.  
  Needs `--convert_path`

- `--convert_path`, `-c`  
  Specifies the directory where converted files will be saved.  

### Example usage:
```
python image_converter.py --source_files "/path/to/dir/photo1.png" (-s)  
                          --source_dir "/path/to/dir/" (-d)  
                          --convert_path "/path/to/dir/convert" (-c)  
                          --organization img (-o)  
                          --convert_to jpeg (-f)  
```

