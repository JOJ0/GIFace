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
    print(f"Processing first, catching face: {image_paths[0]}")
    recognize_face = face_recognition.load_image_file(image_paths[0])
    the_face_encoding = face_recognition.face_encodings(recognize_face)[0]
    print(f"Debug: This is the faces encoding: {the_face_encoding}")
    # Process rest of pictures
    images = []
    for image in image_paths[1:]:
        print(f"Processing {image}")
        image_of_people = face_recognition.load_image_file(image)
        unknown_face_locations = face_recognition.face_locations(image_of_people)
        for face_location in unknown_face_locations:  # Loop found faces
            top, right, bottom, left = face_location  # Save coordinates
            found_face = image_of_people[top:bottom, left:right]
            # Check if it's the face we are looking for
            try:
                compared = face_recognition.compare_faces(
                        [the_face_encoding], found_face)
            except ValueError as verr:
                print(f"ValueError catched: {verr}")
            except IndexError as ierr:
                print(f"ValueError catched: {ierr}")

            if compared[0] is True:
                print(f"Found matching face in {image}")
                im = Image.fromarray(found_face)
                im.thumbnail(size)  # Streamline size,
                images.append(im)  # and finally save to images list
            else:
                print(f"Face not matching in {image}")

    # Save gif
    images[1].save('final.gif', save_all=True, append_images=images[1:],
            duration=300, loop=1)

