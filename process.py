# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import codecs
import os
import sys

from lxml import etree
from treetaggerwrapper import TreeTagger, TreeTaggerError, NotTag, make_tags

# Define the pos attribute per language, to stay in line with EuroParl.
POS_TAGS = {'de': 'tree', 'en': 'tree', 'es': 'tree', 'fr': 'pos', 'it': 'pos', 'nl': 'tree', 'pl': 'tree', 'ru': 'tree'}
SENT_TAGS = {'de': '$.', 'en': 'SENT', 'es': 'FS', 'fr': 'SENT', 'it': 'SENT', 'nl': '$.', 'pl': 'interp', 'ru': 'SENT'}


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def instantiate_tagger(language):
    # Instantiate a tagger
    try:
        return TreeTagger(TAGLANG=language)
    except TreeTaggerError as e:
        eprint(e)


def from_xml(input_files, language):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        tree = etree.parse(in_file)

        for sentence in tree.xpath('//s'):
            # Retrieve all words in the sentence
            s = ''
            prev_word = ' '
            words = sentence.xpath('./w')
            for word in words:
                if word.text[0] in [',', '.', '\'']:  # Dealing with things like "'s", "Mr." and "n't"
                    s += word.text
                elif language in ['fr', 'it'] and prev_word[-1] in ['\'']:  # Dealing with things like "j'ai"
                    s += word.text
                elif language in ['fr'] and word.text.endswith(('-toi','-vous', '-ci', u'-là')):  # Dealing with things like "voulez-vous"
                    s += ' ' + word.text.split('-')[0].lower()
                else:
                    s += ' ' + word.text
                prev_word = word.text

            # Special case for Dutch with cases like "'s middags".
            if language == 'nl':
                s = s.replace('\'s ', ' des ')
            # Special cases for French
            elif language == 'fr':
                s = s.replace('aujourd\'hui', 'aujourd\' hui')
                s = s.replace('Aujourd\'hui', 'Aujourd hui')

                s = s.replace('d\'abord', 'de abord')

                s = s.replace('M.', 'Mr')
                s = s.replace('X.', 'X')
            # Special cases for Italian
            elif language == 'it':
                s = s.replace('C\'', 'Ce ')
                s = s.replace('c\'', 'ce ')
                s = s.replace('N\'', 'Ne ')
                s = s.replace('n\'', 'ne ')
                s = s.replace('v\'', 've ')
                s = s.replace('quell\'', 'quelle ')
                s = s.replace('tant\'', 'tante ')

                s = s.replace('po\'', 'poco \' ')
                s = s.replace('di\'', 'di \' ')

            # Tag/lemmatize the sentence
            tags = make_tags(tagger.tag_text(unicode(s)))

            # Add the tags and lemmata back to the words
            for n, word in enumerate(words):
                try:
                    if type(tags[n]) != NotTag:
                        word.attrib[POS_TAGS.get(language, 'tree')] = tags[n].pos
                        word.attrib['lem'] = tags[n].lemma
                except IndexError:
                    # The end of a sentence is sometimes not properly recognized, deal as a special case.
                    if word.text == '.':
                        word.attrib[POS_TAGS.get(language, 'tree')] = SENT_TAGS.get(language, 'SENT')
                        word.attrib['lem'] = '.'
                    # Otherwise, print the sentence
                    else:
                        eprint('IndexError: {}'.format(s))

        # Output the result to a file
        filename, ext = os.path.splitext(in_file)
        filename += '-out' + ext
        with codecs.open(filename, 'w') as out_file:
            out_file.write(etree.tostring(tree, encoding='utf-8', pretty_print=True, xml_declaration=True))


def from_txt(input_files, language):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        with codecs.open(in_file, 'r', encoding='utf-8') as f:
            lines = []
            for line in f:
                if line.strip():
                    lines.append('\n'.join(tagger.tag_text(line)))
                else:
                    lines.append('\n\n')

            filename, ext = os.path.splitext(in_file)
            filename += '-out' + ext
            with codecs.open(filename, 'w', encoding='utf-8') as g:
                g.writelines(lines)


if __name__ == "__main__":
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description='Tag/lemmatize .xml/.txt-files.')
    parser.add_argument('file_type', type=str, help='Your type of file: xml/txt')
    parser.add_argument('language', type=str, help='Your language of choice')
    parser.add_argument('input_files', type=str, nargs='+', help='The input files')
    args = parser.parse_args()

    # Start the process based on the file_type
    if args.file_type == 'xml':
        from_xml(args.input_files, args.language)
    elif args.file_type == 'txt':
        from_txt(args.input_files, args.language)
    else:
        eprint('Unknown value for file_type, should be either xml or txt')
