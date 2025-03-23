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
Filtering non image files before adding them to mapping_dict
"""

MAPPING_DICT = {"files": {}}

"""
MAPPING_DICT = {
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


FORMATS_SUPPORTED = [
    "All",        # Will choose all formats below
    "JPEG",       # Joint Photographic Experts Group (JPEG/JPG)
    "PNG",        # Portable Network Graphics
    "GIF",        # Graphics Interchange Format
    "TIFF",       # Tagged Image img Format
    "WEBP",       # WebP Image Format
    "JPEG2000",   # JPEG 2000 (JP2, J2K, JPC, JPF, JPG2)
    "BMP",        # Bitmap
    "ICO",        # Icon Format
    "PCX",        # PCX Image Format
    "EPS",        # Encapsulated PostScript
    "DDS",        # DirectDraw Surface
    "DIB",        # Device Independent Bitmap
    "PPM",        # Portable Pixmap (PGM, PBM, PNM)
    "XBM",        # X11 Bitmap
    "IM",         # ImageMagick format
    "SGI",        # Silicon Graphics Image (RGB, RGBA, BW)
    "SPIDER",     # SPIDER Image Format
    "TGA",        # Truevision Targa Image
    "MSP",        # MSP Image Format
]


def organization_by_image():
    """
    Ask to the user how he want the organization inside the convert folder
    Returns True if image organization is choosen
    Uses questionary library
    """
    organization_question = questionary.select(
        'How do you want your directories organization ? ', choices=["By image", "By format"]).ask()
    if organization_question == "By image":
        return True
    return False


def ask_formats_to_convert():  # NEEDED
    """
    Function that use questionary library to let the user
    choosing in which formats converting the selected images
    Adds "convert_to" in MAPPING_DICT
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
        MAPPING_DICT.update({"convert_to": formats_choosen})
        return


def select_source_dir():
    """
    Opens a window to select the path where are located all the images to convert
    Returns the corresponding path
    TODO: add source directory in MAPPING_DICT instead of returning it
    """
    root = tk.Tk()
    root.withdraw()  # Hide Tkinter main window
    source_dir = filedialog.askdirectory(title="Select source directory")
    return source_dir


def img_to_convert(source_dir, mapping_dict):
    """
    Adds a dict for each file  to MAPPING_DICT["files]:
     { "picture1.png": {"file_stem": "picture1"} }
    Selects only files

    Args:
        source_dir: source directory from select_source_dir func | String
        mapping_dict: dictionary

    TODO: Remove all non-picture files too
    """
    # Look in source path for img only
    for file in os.listdir(source_dir):
        if os.path.isfile(os.path.join(source_dir, file)):
            img_dict = {"file_stem": file.split('.')[0]}
            mapping_dict["files"][file] = img_dict


def create_convert_paths(source_dir, by_image_organization, mapping_dict):
    """
    If organization_by_image is True:
        Adds destination path for each file with form Path/convert/file_stem
        as destination directory
        to MAPPING_DICT["files"][file]
    OR
    If organization_by_image is False:
        Adds desination parent path with form Path/convert/ to MAPPING_DICT

    Args:
        source_dir: source directory from select_source_dir func | String
        by_image_organization: from organization_by_image func |  Bool
        mapping_dict: dictionary
    """

    def _make_dir(path):
        """
        Creates directory with a path arg
        """
        if not os.path.exists(path):
            os.makedirs(path)

    convert_dir = f'{source_dir}/convert'
    # Directories organization by format or by file
    if by_image_organization:
        # Put all file_stem values in a list
        for file in mapping_dict["files"].values():
            file_stem = file["file_stem"]
            dir_destination = f'{convert_dir}/{file_stem}'
            _make_dir(dir_destination)
            file["dir_destination"] = dir_destination
    else:
        formats_dirs = mapping_dict.get("convert_to")
        for format_dir in formats_dirs:
            dir_destination = f'{convert_dir}/{format_dir}'
            _make_dir(dir_destination)
    mapping_dict["convert_parent_path"] = convert_dir


def convert_images(source_dir, by_image_organization, mapping_dict):
    """
    Converts all images from mapping dict
    Args:
        source_dir: source directory from select_source_dir func | String
        by_image_organization: from organization_by_image func |  Bool
        mapping_dict: dictionary
    TODO:
        convert in RGB or RGBA if image.save fails only
    """

    def _convert_rgba(file, image):
        '''
        Convert RGBA mode to RGB to maximize chances to convert image'
        '''
        if image.mode == 'RGBA':
            print(
                f'{file} is in RGBA mode, converting to RGB before format to maximize chances')
            image = image.convert('RGB')

    if not mapping_dict.get("files"):
        print("No images in directory, or already convert, skipping.")
        return

    convert_path = mapping_dict.get("convert_parent_path")
    for file, values in mapping_dict["files"].items():
        dir_destination = values.get("dir_destination")
        file_stem = values.get("file_stem")

        print(f'CONVERTING {file}...')

        # TODO: avoid this try except block by filtering non image files in mapping_dict
        try:
            image = Image.open(f'{source_dir}/{file}')
        except UnidentifiedImageError as e:
            print(f'{file_stem} is not an image, skipping... {e}')
            continue

        _convert_rgba(file, image)

        # save new img with new extension choosen
        for convert_format in mapping_dict.get("convert_to"):
            try:
                if by_image_organization:
                    image.save(f'{dir_destination}/{file_stem}.{convert_format.lower()}',
                               format=convert_format)
                else:
                    image.save(
                        f'{convert_path}/{convert_format}/{file_stem}.{convert_format.lower()}',
                        format=convert_format)

            except (ValueError, OSError) as e:
                print(f'Cannot convert {file_stem} to {convert_format}: {e}')

            print(f"{file_stem}.{convert_format} done.")


def main():
    """
    Calls all functions to fill MAPPING_DICT, 
    then convert all images in mapping dict with all formats in same dict
    TODO:
        MAPPING_DICT can break if functions are called in another sequence
        Will be better if functions that returns nothing are directly called by others
        MAPPING_DICT is not a constant variable, change naming or way it works

    """
    # Fill MAPPING_DICT
    by_image_organization = organization_by_image()
    ask_formats_to_convert()
    source_dir = select_source_dir()
    img_to_convert(source_dir, MAPPING_DICT)
    create_convert_paths(
        source_dir, by_image_organization, MAPPING_DICT)

    # Convert all images in MAPPING_DICT
    convert_images(source_dir, by_image_organization, MAPPING_DICT)

    print("all images done.")


if __name__ == '__main__':
    main()
