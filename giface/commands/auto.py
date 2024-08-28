"""auto subcommand module
"""
import click
from pathlib import Path
import yaml
from PIL import Image
import face_recognition
from datetime import datetime
from PIL import ImageFont
from PIL import ImageDraw
from pillow_heif import register_heif_opener

from giface.config import valid_conf
from giface.cropped_thumb import cropped_thumbnail


register_heif_opener()

@click.command()
@click.argument('source_images', nargs=-1, type=click.Path(exists=True))
@click.option('--size', '-s', default='128', type=int)
@click.option('--tolerance', '-t', default='0.6', type=float)
@click.option('--outfile', '-o', type=str)
@click.option('--first', type=click.Path(exists=True),
              help='''Specify`the first` image. Otherwise simply the first of
              source_images will be used.''')
def auto(source_images, size, outfile, first, tolerance):
    """Generates animated GIF from a bunch of pictures

    while using the first found face to recognize in subsequent pics.

    Takes a list of pictures as argument. Use shell globbing to pass a whole
    folder of pics (use /path/*)
    """
    def add_watermark(picture, color, position):
        "Adds a watermark in the given rgb color (3 value tuple)."
        wm_text = "joj0/giface"
        watermark_image = picture.copy()
        draw = ImageDraw.Draw(watermark_image)

        # Find center of image,
        width, height = picture.size
        xcent, ycent = int(width / 2), int(height / 2)
        # and decide on a font size
        font_size = ycent if xcent > ycent else xcent
        # position vertically, just a little from the left
        xtext = width - 2
        # position horizontally, just a few px from the top or the bottom
        ytext = 5 if position == 'top' else height - 5
        font = ImageFont.truetype(
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
                int(font_size/6))
        # Add watermark
        draw.text((xtext, ytext), wm_text, fill=color, font=font, anchor='rm')
        return watermark_image

    final_size = (size, size)
    # While gathering list of files, filter out non-valid ones
    image_paths = [
            image for image in source_images
            if (str(Path(image).suffix).lower()
                in ['.jpg', '.jpeg', '.png', '.heic'])
    ]
    if first:
        image_paths.insert(0, first)
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
        unknown_face_locations = face_recognition.face_locations(unknown_image, number_of_times_to_upsample=1, model="hog")
        for i, location in enumerate(unknown_face_locations):
            # Get face encoding for found face location by list id
            unknown_face_encoding = face_recognition.face_encodings(
                unknown_image)[i]
            # Check if it's the face we are looking for
            try:
                compared = face_recognition.compare_faces(
                        [the_face_encoding], unknown_face_encoding, tolerance=tolerance)
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
                # print("Debug: Img size:")
                # print(im.size)
                images.append(im)  # and finally save to images list
            else:
                print(f"Not-matching face in {image}")
        # After each picture, make some space for readability
        print('')

    # Add watermark to the second half of the pics
    wm_color = (255, 255, 255)
    markfrom = len(images) / 2
    position = 'top'
    for cnt,img in enumerate(images):
        if cnt > markfrom:
            images[cnt] = add_watermark(images[cnt], wm_color, position)


    if not outfile:
        name = "GIFace_" + datetime.now().strftime('%m-%d-%Y_%H-%M') + '.gif'
        outfile = Path(Path.home() / 'Pictures') / name
    # Save gif
    print(f"Saving to {outfile}")
    images[0].save(outfile, save_all=True, append_images=images[1:],
            duration=120, loop=0)

