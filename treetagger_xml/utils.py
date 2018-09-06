# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

from treetaggerwrapper import TreeTagger, TreeTaggerError


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def instantiate_tagger(language):
    # Instantiate a tagger
    try:
        return TreeTagger(TAGLANG=language)
    except TreeTaggerError as e:
        eprint(e)
