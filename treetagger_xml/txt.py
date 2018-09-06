# -*- coding: utf-8 -*-

import codecs
import os

from utils import instantiate_tagger


def from_txt(input_files, language, in_place=False):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        with codecs.open(in_file, 'r', encoding='utf-8') as f:
            lines = []
            for line in f:
                if line.strip():
                    lines.append('\n'.join(tagger.tag_text(line)))

                lines.append('\n\n')

        if in_place:
            filename = in_file
        else:
            filename, ext = os.path.splitext(in_file)
            filename += '-out' + ext
        with codecs.open(filename, 'w', encoding='utf-8') as g:
            g.writelines(lines)
