import argparse
import os

from lxml import etree
from treetaggerwrapper import TreeTagger, NotTag, make_tags

# Define the pos attribute per language, to stay in line with EuroParl. TODO: is this necessary?
POS_TAGS = {'de': 'tree', 'en': 'pos', 'es': 'tree', 'fr': 'pos', 'nl': 'tree'}

# Parse the command-line arguments
parser = argparse.ArgumentParser(description='Tag/lemmatize .xml-files.')
parser.add_argument('language', type=str, help='Your language of choice')
parser.add_argument('input_files', type=str, nargs='+', help='The input files')
args = parser.parse_args()

# Instantiate a tagger
tagger = TreeTagger(TAGLANG=args.language)

for in_file in args.input_files:
    tree = etree.parse(in_file)

    for sentence in tree.xpath('//s'):
        # Retrieve all words in the sentence
        s = ''
        words = sentence.xpath('./w')
        for word in words:
            s += word.text + ' '
        
        # Tag/lemmatize the sentence
        tags = make_tags(tagger.tag_text(unicode(s)))

        # Add the tags and lemmata back to the words
        for n, word in enumerate(words):
            if type(tags[n]) != NotTag:
                word.attrib[POS_TAGS.get(args.language, 'pos')] = tags[n].pos
                word.attrib['lem'] = tags[n].lemma

    # Output the result to a file
    filename, ext = os.path.splitext(in_file)
    filename += '-out' + ext
    with open(filename, 'wb') as out_file:
        out_file.write(etree.tostring(tree, encoding='utf-8', pretty_print=True, xml_declaration=True))
