import argparse
import os
import string

from lxml import etree
from treetaggerwrapper import TreeTagger, NotTag, make_tags

# Define the pos attribute per language, to stay in line with EuroParl.
POS_TAGS = {'de': 'tree', 'en': 'tree', 'es': 'tree', 'fr': 'pos', 'nl': 'tree'}
SENT_TAGS = {'de': '$.', 'en': 'SENT', 'es': 'FS', 'fr': 'SENT', 'nl': '$.'}

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
        prev_word = ' '
        words = sentence.xpath('./w')
        for word in words:
            if word.text[0] in [',', '.', '\'']:  # Dealing with things like "'s", "Mr." and "n't"
                s += word.text
            elif args.language == 'fr' and prev_word[-1] in ['\'']:  # Dealing with things like "j'ai"
                s += word.text
            else:
                s += ' ' + word.text
            prev_word = s
       
        # Special case for Dutch with cases like "'s middags".
        if args.language == 'nl':
            s = s.replace('\'s ', ' des ')
        
        # Tag/lemmatize the sentence
        tags = make_tags(tagger.tag_text(unicode(s)))

        # Add the tags and lemmata back to the words
        for n, word in enumerate(words):
            try:
                if type(tags[n]) != NotTag:
                    word.attrib[POS_TAGS.get(args.language, 'tree')] = tags[n].pos
                    word.attrib['lem'] = tags[n].lemma
            except IndexError:
                # The end of a sentence is sometimes not properly recognized, deal as a special case.
                if word.text == '.':
                    word.attrib[POS_TAGS.get(args.language, 'tree')] = SENT_TAGS.get(args.language, 'SENT')
                    word.attrib['lem'] = '.'
                # Otherwise, print the sentence
                else:
                    print u'IndexError: {}'.format(s)

    # Output the result to a file
    filename, ext = os.path.splitext(in_file)
    filename += '-out' + ext
    with open(filename, 'wb') as out_file:
        out_file.write(etree.tostring(tree, encoding='utf-8', pretty_print=True, xml_declaration=True))
