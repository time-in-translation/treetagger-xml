# -*- coding: utf-8 -*-

import codecs
import os

from .utils import instantiate_tagger
from .treetagger2opus import process as tag2xml


def from_txt(input_files, language, in_place=False):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        process_single(tagger, language, in_file, in_place)


def process_single(tagger, language, in_file, in_place=False, out_file=None):
    with codecs.open(in_file, 'r', encoding='utf-8') as f:
        lines = []
        for line in f:
            if line.strip():
                lines.append('\n'.join(tagger.tag_text(line)))

            lines.append('\n\n')

    if in_place:
        tag_file = in_file
    else:
        tag_file = os.path.splitext(in_file)[0] + '.tag'

    with codecs.open(tag_file, 'w', encoding='utf-8') as g:
        g.writelines(lines)

    if not out_file:
        out_file = os.path.splitext(tag_file)[0] + '.xml'

    tag2xml(language, tag_file, out_file)
