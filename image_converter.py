import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, UnidentifiedImageError
import questionary

"""
TODO:
Multithreading to speed up conversion?
Retrieve the correct (and complete) format list
Create a dynamic format list based on the source image?
Filtering non image files before adding them to convert_map
"""

FORMATS_SUPPORTED = [
    "All",        # Will choose all formats below
    "JPEG",       # Joint Photographic Experts Group (JPEG/JPG)
    "PNG",        # Portable Network Graphics
    "GIF",        # Graphics Interchange Format
    "PDF",        # Portable Document Format
    "TIFF",       # Tagged Image img Format
    "WEBP",       # WebP Image Format
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

'''
MODES = [
    "1",
    "CMYK",
    "F",
    "HSV",
    "I",
    "I;16",
    "I;16B",
    "I;16L",
    "I;16N",
    "L",
    "LA",
    "La",
    "LAB",
    "P",
    "PA",
    "RGB",
    "RGBA",
    "RGBa",
    "RGBX",
    "YCbCr",
]
'''

CONVERT_MAP = {"files": {}}

"""
CONVERT_MAP = {
    "files":
    {
        "photo1.png":
        {"file_stem": "photo1",  #(only effective if organization_by_image func is True )
         "dir_destination": "C:/Users/User/Pictures/convert/photo"
         },
        "photo2.png": {...}
    },
    "convert_to": ["JPEG", "PNG", "GIF", "...."],
    "convert_parent_path": "C:/Users/User/Pictures/convert/photo"
}
"""


def ask_convert_scope():
    """
    Ask to the user if he wants to convert one/several file(s) or a whole dir
    Returns response
    """
    scope_question = questionary.select(
        'How to select files',
        choices=[
            {"name": "Selecting file by file", "value": "file"},
            {"name": "A whole directory", "value": "dir"}
        ]
    ).ask()
    if scope_question == "file":
        return "file"
    return "directory"


def organization_by_image():
    """
    Ask to the user how he want the organization inside the convert folder
    Returns True if image organization is choosen
    Uses questionary library
    """
    organization_question = questionary.select(
        'How do you want your directories organization ? ',
        choices=[
            {"name": "By image", "value": "img"},
            {"name": "By format", "value": "format"}
        ]
    ).ask()

    if organization_question == "img":
        return True
    return False


def ask_formats_to_convert(convert_map):  # NEEDED
    """
    Function that use questionary library to let the user
    choosing in which formats converting the selected images
    Adds "convert_to" in convert_map
    """

    def _confirm_choice():
        """
        Ask user to confirm choices
        Generates selection with questionary library
        """
        choice_confirmation = questionary.select(
            'Confirm choices ?', choices=["yes", "no"]).ask()
        if choice_confirmation == "yes":
            return True
        return False

    while True:
        # Generate checkbox to choose formats from list
        formats_choosen = questionary.checkbox(
            "Select the formats ", choices=FORMATS_SUPPORTED).ask()

        if not formats_choosen:
            print("No formats specified, use spacebar to select")
            continue

        if "All" in formats_choosen:
            print(
                '!WARNING!: You have selected "All", '
                'which will converts your images to all 19 formats'
            )

            # Returns all formats if user confirm choice "All"
            formats_choosen = FORMATS_SUPPORTED.copy()
            formats_choosen.remove("All")

        print(f' You have selected {formats_choosen}')
        if not _confirm_choice():
            continue
        convert_map.update({"convert_to": formats_choosen})
        return


def select_source(convert_scope, convert_map):
    """
    Opens a window to select the path where are located all the images to convert
    Returns the corresponding path
    TODO: add source directory in convert_map instead of returning it
    """
    root = tk.Tk()
    root.withdraw()  # Hide Tkinter main window
    if convert_scope == "file":
        source = list(filedialog.askopenfilenames(
            title="Select source file"))

        parent_path = os.path.dirname(source[0])
        # Keep only file names
        for n, file in enumerate(source):
            source[n] = os.path.basename(file)

    else:
        parent_path = filedialog.askdirectory(
            title="Select source directory")
        source = parent_path

    convert_map["parent_path"] = parent_path
    convert_map["convert_parent_path"] = f'{convert_map.get("parent_path")}/convert'
    convert_map["source"] = source
    return convert_map


def img_to_convert(source, convert_map):
    """
    Adds a dict for each file  to convert_map["files]:
     { "picture1.png": {"file_stem": "picture1"} }
    Selects only files

    Args:
        source_dir: source directory from select_source func | String
        convert_map: dictionary

    TODO: Remove all non-picture files too
    """

    def _fill_map_dict_with_files(file):
        file_stem, extension = os.path.splitext(file)
        img_dict = {"file_stem": file_stem}
        convert_map["files"][file] = img_dict

    if isinstance(source, list):
        for file in source:
            _fill_map_dict_with_files(file)
        return convert_map

    # Look in source path for files only
    for file in os.listdir(source):
        if os.path.isfile(os.path.join(source, file)):
            _fill_map_dict_with_files(file)
    return convert_map


def create_convert_paths(by_image_organization, convert_map):
    """
    If organization_by_image is True:
        Adds destination path for each file with form Path/convert/file_stem
        as destination directory
        to convert_map["files"][file]
    OR
    If organization_by_image is False:
        Adds desination parent path with form Path/convert/ to convert_map

    Args:
        source_dir: source directory from select_source func | String
        by_image_organization: from organization_by_image func |  Bool
        convert_map: dictionary
    """

    def _make_dir(path):
        """
        Creates directory with a path arg
        """
        if not os.path.exists(path):
            os.makedirs(path)

    convert_dir = convert_map.get(
        "convert_parent_path", f'{os.getcwd()}/convert')
    # Directories organization by format or by file
    if by_image_organization:
        # Put all file_stem values in a list
        for file in convert_map["files"].values():
            dir_destination = f'{convert_dir}/{file["file_stem"]}'
            _make_dir(dir_destination)
            file["dir_destination"] = dir_destination
    else:
        formats_dirs = convert_map.get("convert_to")
        for format_dir in formats_dirs:
            dir_destination = f'{convert_dir}/{format_dir}'
            _make_dir(dir_destination)


def convert_images(by_image_organization, convert_map):
    """
    Converts all images from mapping dict
    Args:
        source_dir: source directory from select_source func | String
        by_image_organization: from organization_by_image func |  Bool
        convert_map: dictionary
    TODO:
        convert in RGB or RGBA if image.save fails only
    """

    def _convert_img_mode(file, image):
        '''
        Convert RGBA/RGB mode to maximize chances to convert'
        '''
        mode = image.mode
        print(
            f' Cannot convert {file} because it is in {mode}, '
            f'converting to RGB/RGBA format to maximize chances')
        if mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode == 'RGB':
            image = image.convert('RGBA')
        return image

    def _save_image(by_image_organization, image,
                    dir_destination, file_stem, convert_format, convert_path):
        if by_image_organization:
            image.save(f'{dir_destination}/{file_stem}.{convert_format}',
                       format=convert_format)
        else:
            image.save(
                f'{convert_path}/{convert_format}/{file_stem}.{convert_format}',
                format=convert_format)

    if not convert_map.get("files"):
        print("No images in directory, or already convert, skipping.")
        return

    convert_path = convert_map.get("convert_parent_path")
    for file, file_values in convert_map["files"].items():
        dir_destination = file_values.get("dir_destination")
        file_stem = file_values.get("file_stem")

        print(f'CONVERTING {file}...')

        # TODO: avoid this try except block by filtering non image files in convert_map
        try:
            image = Image.open(f'{convert_map.get("parent_path")}/{file}')
        except UnidentifiedImageError as e:
            print(f'{file_values.get("file_stem")} is not an image, skipping... {e}')
            continue

        # save new img with new extension choosen
        for convert_format in convert_map.get("convert_to"):
            try:
                _save_image(by_image_organization, image,
                            dir_destination, file_stem, convert_format, convert_path)
                print(f"{file_stem}.{convert_format} done.")
            except (ValueError, OSError):
                try:
                    image = _convert_img_mode(file, image)
                    _save_image(by_image_organization, image,
                                dir_destination, file_stem, convert_format, convert_path)
                    print(f"{file_stem}.{convert_format} done.")
                except (ValueError, OSError) as e:
                    print(
                        f'Cannot convert {file_stem} to {convert_format} neither: {e}, skipping..')


def main():
    """
    Calls all functions to fill convert_map,
    then convert all images in mapping dict with all formats in same dict
    TODO:
        convert_map can break if functions are called in another sequence
        Will be better if functions that returns nothing are directly called by others
        CONVERT_MAP is not a constant variable, change naming or way it works

    """
    # Fill convert_map
    by_image_organization = organization_by_image()
    ask_formats_to_convert(CONVERT_MAP)
    select_source(ask_convert_scope(), CONVERT_MAP)
    source_dir = CONVERT_MAP.get("source")
    img_to_convert(source_dir, CONVERT_MAP)
    create_convert_paths(by_image_organization, CONVERT_MAP)

    # # Convert all images in convert_map
    convert_images(by_image_organization, CONVERT_MAP)

    print("all images done.")


if __name__ == '__main__':
    main()
