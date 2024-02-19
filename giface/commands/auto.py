"""auto subcommand module
"""
import click
from pathlib import Path
import yaml
from PIL import Image
import face_recognition

from giface.config import valid_conf


@click.command()
@click.argument('source_images', nargs=-1, type=click.Path(exists=True))
# @click.argument('post_md_file', nargs=1, type=click.Path(exists=True))
# @click.option('--write', '-w', is_flag=True,
#               help="Do the conversion. Dry-run is default.")
# @click.option('--force', '-f', is_flag=True,
#               help="Overwrite if existing already.")
# @click.option('--gallery', '-g', type=str,
#               help="Create collection markdown files for photo gallery as well.")  # noqa
# @click.option('--start', '-s', type=int, default=1, show_default=True,
#               help="Start naming pics and gallery files with this number.")
def auto(source_images):
    """ Generate a GIF from a bunch of pictures

    Takes a list of pictures as argument. Use shell globbing to pass a whole
    folder of pics (use /path/*)
    """
    # images = [Image.open(fn) for fn in file_names]
    size = (666,666)
    new_width = 333
    new_height = 333

    images = []
    for image in source_images:
        # Filter out non-valid files
        if (
            Path(image).is_dir()
            or str(Path(image).suffix).lower() not in ['.jpg', '.jpeg', '.png']
        ):
            continue

        image_of_people = face_recognition.load_image_file(image)
        unknown_face_locations = face_recognition.face_locations(image_of_people)
        for face_location in unknown_face_locations:
            top, right, bottom, left = face_location
            face_image = image_of_people[top:bottom, left:right]
            im = Image.fromarray(face_image)

        # Prepare image for GIF and add to list
        im.thumbnail(size)  # Streamline size
        images.append(im)


    images[1].save('final.gif', save_all=True, append_images=images[1:],
            duration=333, loop=1)

