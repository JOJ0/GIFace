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
    """Generates animated GIF from a bunch of pictures

    while using the first found face to recognize in subsequent pics.

    Takes a list of pictures as argument. Use shell globbing to pass a whole
    folder of pics (use /path/*)
    """
    size = (333, 333)
    new_width = 333
    new_height = 333
    # Filter out non-valid files
    image_paths = [
            image for image in source_images
            if (str(Path(image).suffix).lower()
                in ['.jpg', '.jpeg', '.png'])
    ]
    # Use first picture as example for face to recognize
    recognize_face = face_recognition.load_image_file(image_paths[0])
    the_face_encoding = face_recognition.face_encodings(recognize_face)[0]
    # Process rest of pictures
    images = []
    for image in image_paths:
        image_of_people = face_recognition.load_image_file(image)
        unknown_face_locations = face_recognition.face_locations(image_of_people)
        for face_location in unknown_face_locations:  # Loop found faces
            top, right, bottom, left = face_location  # Save coordinates
            found_face = image_of_people[top:bottom, left:right]
            # Check if it's the face we are looking for
            compared = face_recognition.compare_faces([the_face_encoding], found_face)
            if compared[0] is True:
                im = Image.fromarray(found_face)
                im.thumbnail(size)  # Streamline size,
                images.append(im)  # and finally save to images list

    # Save gif
    images[1].save('final.gif', save_all=True, append_images=images[1:],
            duration=300, loop=1)

