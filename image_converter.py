import sys
import argparse
from pathlib import Path
import shutil
import pillow_avif
import tkinter as tk
from tkinter import filedialog
from PIL import Image, UnidentifiedImageError
import questionary

"""
TODO:
Multithreading to speed up conversion?
Create file log ?
Add newer formats conversion(pillow_avif, pyheif)
"""

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

"""
CONVERT_MAP =
{'files':
    {'photo1.png':
        {'file_stem': 'photo1',
            'dir_destination': 'C:/Users/user/pictures/convert', 'parent_path': "/home/pictures/"}
    },
    {'photo2'.png} : {...},
 'organization': 'img',
 'convert_to': ['JPEG'],
 'convert_scope': 'file',
 'source_files': ['photo1.png', 'photo2.png'],
 'source_dir': 'C:/Users/rafif/Pictures',
 'parent_path': 'C:/Users/rafif/Pictures',
 'convert_path': 'C:/Users/rafif/Pictures/convert'
}
"""


def build_with_args(map_dict):
    """
    Returns map_dict with arguments given, fill keys with None if no args
    """
    parser = argparse.ArgumentParser("convert map contruction", add_help=False)
    parser.add_argument('-o', "--organization",
                        help="Set organization type", choices=["img", "format"], type=str)
    parser.add_argument('-f', "--convert_to",
                        help="List to select conversion formats,"
                        "check help to see supported formats",
                        choices=FORMATS_SUPPORTED, type=str.upper, nargs='+')
    parser.add_argument('-s', "--source_files",
                        help="List of files to convert separated by spaces", nargs='+', type=Path)
    parser.add_argument(
        '-d', "--source_dir", help="Path for source directory,"
        "all images in it will be converted", type=Path)
    parser.add_argument('-c', "--convert_path",
                        help="Path where to store converted files", type=Path)
    parser.add_argument("-h", "--help", action="help",
                        help=f'Supported formats {FORMATS_SUPPORTED}')
    args = parser.parse_args()

    if (args.source_dir or args.source_files) and not args.convert_path:
        parser.print_help()
        print("\nERROR: '--convert_path' is required if either"
              " '--source_dir' or '--source_files' is provided.")
        sys.exit(1)  # Exit the program with an error

    args_dict = {k: v for k, v in vars(args).items() if v is not None}
    map_dict.update(args_dict)
    return map_dict


def ask_organization(map_dict):
    """
    Ask to the user how he want the organization inside the convert folder
    Returns True if image organization is choosen
    Uses questionary library
    """
    if not map_dict.get("organization"):
        organization_question = questionary.select(
            'How do you want your directories organization ? ',
            choices=[
                {"name": "By image", "value": "img"},
                {"name": "By format", "value": "format"}
            ]
        ).ask()

        map_dict["organization"] = organization_question
    return map_dict


def ask_wanted_formats(map_dict):  # NEEDED
    """
    Function that use questionary library to let the user
    choosing in which formats converting the selected images
    Adds "convert_to" in convert_map
    """

    def _update_all_choices(choices):
        if "ALL" in choices or "all" in choices:
            print(
                '!WARNING!: You have selected "All", '
                'which will converts your images to all 19 formats'
            )

            # Returns all formats if user confirm choice "All"
            choices = [
                format for format in FORMATS_SUPPORTED if format not in {"ALL", "all"}]
        return choices

    if map_dict.get("convert_to"):
        map_dict["convert_to"] = _update_all_choices(
            map_dict.get("convert_to"))
        return map_dict

    while True:
        # Generate checkbox to choose formats from list
        formats_choosen = questionary.checkbox(
            "Select the formats ", choices=FORMATS_SUPPORTED).ask()

        if not formats_choosen:
            print("No formats specified, use spacebar to select")
            continue

        formats_choosen = _update_all_choices(formats_choosen)

        if questionary.confirm(f"You selected {formats_choosen}. Confirm?").ask():
            map_dict["convert_to"] = formats_choosen
            return map_dict


def ask_convert_scope(map_dict):
    """
    Ask to the user if he wants to convert one/several file(s) or a whole dir
    Returns response
    """
    # Check if user added source_dir or source_files arguments
    if not any(map_dict.get(key) for key in ("source_files", "source_dir")):
        scope_question = questionary.select(
            'How to select files',
            choices=[
                {"name": "Selecting file by file", "value": "file"},
                {"name": "A whole directory", "value": "dir"}
            ]
        ).ask()
        map_dict["convert_scope"] = scope_question
    return map_dict


def ask_select_source(map_dict):
    """
    Opens a window to select the path where are located all the images to convert
    Returns the corresponding path
    """

    def _fill_map_dict_with_files(file):
        # Check pathlib attributes
        parent_path = file.parent
        file_stem = file.stem
        img_dict = {file.name: {
            "file_stem": file_stem,
            "parent_path": parent_path
        }}
        map_dict["files"].update(img_dict)
        if not map_dict.get("convert_path"):
            map_dict["convert_path"] = f'{parent_path}/convert'

    source_files = {}
    source_dir = None
    scope = map_dict.get("convert_scope")
    if scope:
        root = tk.Tk()
        root.withdraw()  # Hide Tkinter main window
        if scope == "file":
            source_files = list(filedialog.askopenfilenames(
                title="Select source file"))

        elif scope == "dir":
            source_dir = filedialog.askdirectory(
                title="Select source directory")

    # Fill dict with source_files
    for file in source_files or map_dict.get("source_files", {}):
        _fill_map_dict_with_files(Path(file))

    # source_files not needed anymore
    map_dict.pop('source_files', None)

    # Fill dict with files inside source_dir
    source_dir = source_dir or map_dict.get("source_dir")
    if source_dir:
        # filter non-files in Path
        for file in filter(lambda file: file.is_file(), Path(source_dir).iterdir()):
            _fill_map_dict_with_files(Path(file))

    return map_dict


def create_convert_paths(map_dict):
    """
    If organization is img:
        Adds destination path for each file with form Path/convert/file_stem
        as destination directory
        to convert_map["files"][file]
    else:
        Adds desination parent path with form Path/convert/ to convert_map
    """
    def _make_dir(path):
        """
        Creates directory with a path arg
        """
        if not Path.exists(path):
            Path.mkdir(path, parents=True)

    convert_path = map_dict.get(
        "convert_path", f'{Path.cwd()}/convert')
    # Directories organization by format or by file
    if map_dict.get("organization") == "img":
        for file in map_dict["files"].values():
            dir_destination = f'{convert_path}/{file["file_stem"]}'
            _make_dir(Path(dir_destination))
            file["dir_destination"] = dir_destination
    else:
        for format_dir in map_dict.get("convert_to"):
            dir_destination = f'{convert_path}/{format_dir}'
            _make_dir(Path(dir_destination))
    return map_dict


def images_processing(final_map_dict):
    """
    Converts all images from mapping dict
    """

    def _convert_img_mode(file, image, convert_format, original_mode):
        '''
        Convert RGBA/RGB mode to maximize chances to convert'
        '''
        if convert_format in ["XBM", "MSP"]:
            image = image.convert("1")
        elif convert_format == "BLP":
            image = image.convert("P")
        else:
            image = image.convert(original_mode)
            if original_mode == "RGBA":
                image = image.convert("RGB")
            elif original_mode == "RGB":
                image = image.convert("RGBA")

        print(
            f'Cannot convert {file} to {convert_format} because it is in {original_mode}, '
            f'converting to {image.mode} format to maximize chances'
        )
        return image

    def _load_image(file, parent_path):
        print(f'CONVERTING {file}...')
        try:
            image = Image.open(
                f'{parent_path}/{file}')
            return image
        except UnidentifiedImageError as e:
            raise UnidentifiedImageError(
                f'Cannot load {file}, maybe not an image ? skipping... {e}') from e

    def _save_image(map_dict, file_values, convert_format, image):
        organization = map_dict.get("organization")
        convert_path = map_dict.get("convert_path")
        dir_destination = file_values.get("dir_destination")
        file_stem = file_values.get("file_stem")

        if organization == "img":
            image.save(f'{dir_destination}/{file_stem}.{convert_format}',
                       format=convert_format)
        else:
            image.save(
                f'{convert_path}/{convert_format}/{file_stem}.{convert_format}',
                format=convert_format)

    def _convert_image(map_dict):
        # save new img with new extension choosen
        for file, file_values in map_dict.get("files").items():

            try:
                image = _load_image(file, file_values.get("parent_path"))
                original_mode = image.mode
            except UnidentifiedImageError:
                continue

            file_stem = file_values.get("file_stem")

            for convert_format in map_dict.get("convert_to"):
                try:
                    _save_image(map_dict, file_values, convert_format, image)
                    print(f"{file_stem}.{convert_format} done.")
                except (ValueError, OSError):
                    try:
                        image = _convert_img_mode(
                            file, image, convert_format, original_mode)
                        _save_image(map_dict, file_values,
                                    convert_format, image)
                        print(f"{file_stem}.{convert_format} done.")
                    except (ValueError, OSError) as e:
                        print(
                            f'Cannot convert {file_stem}'
                            f'to {convert_format} neither: {e}, skipping..')

    if not final_map_dict.get("files"):
        print("No images in directory, skipping.")
        return

    # Check free disk space before converting each image
    total, used, free = shutil.disk_usage("/")
    free = free // (2**30)
    if free < 5:
        print(
            f'Free disk place is only {free}GiB, stopping conversion below 5GiB')
        return

    _convert_image(final_map_dict)


def main():
    """
    Calls all functions to fill convert_map,
    then convert all images in mapping dict with all formats in same dict
    """
    def pipeline(data, *funcs):
        for func in funcs:
            data = func(data)
        return data

    convert_map = {"files": {}}

    pipeline(
        convert_map,
        build_with_args,
        ask_organization,
        ask_wanted_formats,
        ask_convert_scope,
        ask_select_source,
        create_convert_paths,
        images_processing
    )

    print("all images done.")


if __name__ == '__main__':
    main()
