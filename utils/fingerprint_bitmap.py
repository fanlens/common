#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

from PIL import Image

from db import get_session
from db.models.facebook import FacebookCommentEntry

SIZE = 128


def to_image(comment: FacebookCommentEntry) -> Image:
    positions = comment.meta['fingerprint']
    img = Image.new('RGB', (SIZE, SIZE), 'black')  # create a new black image
    pixels = img.load()  # create the pixel map
    for pos in positions:
        y, x = divmod(pos, SIZE)
        pixels[x, y] = (255, 255, 255)
    return img


def fetch_comment(comment_id: str) -> FacebookCommentEntry:
    with get_session() as session:
        return session.query(FacebookCommentEntry).get(comment_id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='provide id of comment_id')
    parser.add_argument('-id', '--id', type=str, help='the comment_id', required=True)
    args = vars(parser.parse_args())

    comment = fetch_comment(args['id'])
    print(' '.join(comment.data['tokens']))
    img = to_image(comment)
    img.show()
