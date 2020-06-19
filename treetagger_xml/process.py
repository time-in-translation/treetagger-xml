# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse

from treetagger_xml.txt import from_txt
from treetagger_xml.utils import eprint
from treetagger_xml.xml import from_xml


if __name__ == "__main__":
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='Tag/lemmatize .xml/.txt-files.')
    parser.add_argument('file_type', type=str, help='Your type of file: xml/txt')
    parser.add_argument('language', type=str, help='Your language of choice')
    parser.add_argument('input_files', type=str, nargs='+', help='The input files')
    parser.add_argument('--in_place', help='Replace the file in-place', action='store_true')
    args = parser.parse_args()

    # Start the process based on the file_type
    if args.file_type == 'xml':
        from_xml(args.input_files, args.language, args.in_place)
    elif args.file_type == 'txt':
        from_txt(args.input_files, args.language, args.in_place)
    else:
        eprint('Unknown value for file_type, should be either xml or txt')
