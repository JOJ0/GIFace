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
@click.option('--size', '-s', default='100', type=int)
@click.option('--outfile', '-o', type=int)
def auto(source_images, size, outfile):
    """Generates animated GIF from a bunch of pictures

    while using the first found face to recognize in subsequent pics.

    Takes a list of pictures as argument. Use shell globbing to pass a whole
    folder of pics (use /path/*)
    """
    final_size = (size, size)
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
        unknown_image = face_recognition.load_image_file(image)
        unknown_face_locations = face_recognition.face_locations(unknown_image)
        for i, location in enumerate(unknown_face_locations):
            # Get face encoding for found face location by list id
            unknown_face_encoding = face_recognition.face_encodings(
                unknown_image)[i]
            # Check if it's the face we are looking for
            try:
                compared = face_recognition.compare_faces(
                        [the_face_encoding], unknown_face_encoding)
            except IndexError as ierr:
                print(f"IndexError catched: {ierr}")

            # Compare known face with unknown face
            if compared[0] == True:
                print(f"Found matching face in {image}")
                top, right, bottom, left = location
                print("Debug: location:")
                print(location)
                im = Image.fromarray(
                    unknown_image[top:bottom, left:right]
                )
                im.thumbnail(final_size)  # Streamline size
                images.append(im)  # and finally save to images list
            else:
                print(f"Face not matching in {image}")

    if not outfile:
        filename = datetime.now().strftime('%m-/%d-/%Y_%H-%M') + '.png'
        outfile = Path('~/Pictures') / filename
    # Save gif
    images[1].save(outfile, save_all=True, append_images=images[1:],
            duration=100, loop=0)

