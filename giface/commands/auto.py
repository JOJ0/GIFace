"""auto subcommand module
"""
import click
from pathlib import Path
import yaml
from PIL import Image
import face_recognition
from datetime import datetime

from giface.config import valid_conf
from giface.cropped_thumb import cropped_thumbnail


@click.command()
@click.argument('source_images', nargs=-1, type=click.Path(exists=True))
@click.option('--size', '-s', default='128', type=int)
@click.option('--outfile', '-o', type=str)
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
    try:
        recognize_face = face_recognition.load_image_file(image_paths[0])
        the_face_encoding = face_recognition.face_encodings(recognize_face)[0]
        # print(f"Debug: This is the faces encoding: {the_face_encoding}")
    except IndexError as ierr:
        print(f"IndexError: {ierr}. No face in first picture detected, sorry!")
        raise SystemExit(1)

    # Process pictures (including the first one)
    images = []
    for image in image_paths:
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
                print(f"IndexError: {ierr}")

            # Compare known face with unknown face
            if compared[0] == True:
                print(f"Matching face in {image}")
                top, right, bottom, left = location
                # print("Debug: location:")
                # print(location)
                im = Image.fromarray(
                    unknown_image[top:bottom, left:right]
                )
                im = cropped_thumbnail(im, final_size)  # Streamline size
                print("Debug: Img size:")
                print(im.size)
                images.append(im)  # and finally save to images list
            else:
                print(f"Not-matching face in {image}")
        # After each picture, make some space for readability
        print('')

    if not outfile:
        name = "GIFace_" + datetime.now().strftime('%m-%d-%Y_%H-%M') + '.gif'
        outfile = Path(Path.home() / 'Pictures') / name
    # Save gif
    print(f"Saving to {outfile}")
    images[0].save(outfile, save_all=True, append_images=images[1:],
            duration=100, loop=0)

