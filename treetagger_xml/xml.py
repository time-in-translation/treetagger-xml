# -*- coding: utf-8 -*-

import codecs
import os

from lxml import etree
from treetaggerwrapper import make_tags, NotTag

from utils import eprint, instantiate_tagger


POS_TAGS = {'de': 'tree', 'en': 'tree', 'es': 'tree', 'fr': 'pos', 'it': 'pos', 'nl': 'tree', 'pl': 'tree', 'ru': 'tree'}
SENT_TAGS = {'de': '$.', 'en': 'SENT', 'es': 'FS', 'fr': 'SENT', 'it': 'SENT', 'nl': '$.', 'pl': 'interp', 'ru': 'SENT'}


def from_xml(input_files, language, in_place=False):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        process_single(tagger, language, in_file, in_place)


def process_single(tagger, language, in_file, in_place=False):
    tree = etree.parse(in_file)
    for sentence in tree.xpath('//s'):
        # Retrieve all words in the sentence
        s = ''
        prev_word = ' '
        words = sentence.xpath('./w')
        for word in words:
            if word.text[0] in [',', '.', '\'']:  # Dealing with things like "'s", "Mr." and "n't"
                if prev_word.isdigit():  # But don't do this for digits
                    s += ' ' + word.text
                else:
                    s += word.text
            elif language in ['fr', 'it'] and len(prev_word) > 1 and prev_word[-1] in ['\'']:  # Dealing with things like "j'ai"
                s += word.text
            elif language in ['fr'] and word.text.endswith(('-toi', '-vous', '-ci', u'-là')):  # Dealing with things like "voulez-vous"
                s += ' ' + word.text.split('-')[0].lower()
            else:
                s += ' ' + word.text
            prev_word = word.text

        s = apply_replacements(language, s)# Tag/lemmatize the sentence
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
                    eprint(u'IndexError: {}'.format(s))

    # Output the result to a file
    if in_place:
        filename = in_file
    else:
        filename, ext = os.path.splitext(in_file)
        filename += '-out' + ext
    with codecs.open(filename, 'w') as out_file:
        out_file.write(etree.tostring(tree, encoding='utf-8', pretty_print=True, xml_declaration=True))


def apply_replacements(language, s):
    # Special case for Dutch with cases like "'s middags".
    if language == 'nl':
        s = s.replace('\'s ', ' des ')
        s = s.replace('\'t', ' het')
        s = s.replace('\'m', ' hem')
    # Special cases for French
    elif language == 'fr':
        s = s.replace('Aujourd\'hui', 'Jour hui')
        s = s.replace(' aujourd\'hui', ' jour hui')

        s = s.replace(' d\'abord', ' de abord')
        s = s.replace('D\'abord', 'De abord')
        s = s.replace(' d\'accord', ' de accord')
        s = s.replace('D\'accord', 'De accord')
        s = s.replace(u' d\'après', u' de après')
        s = s.replace(u'D\'après', u'De après')
        s = s.replace('D\'ailleurs', 'De ailleurs')
        s = s.replace(' d\'ailleurs', ' de ailleurs')

        s = s.replace(u'C\'est-à-dire', u'Ce est-à-dire')
        s = s.replace(u' c\'est-à-dire', u' ce est-à-dire')

        s = s.replace(' quelqu\'un', ' quelque un')

        s = s.replace('M.', 'Mr')
        s = s.replace('X.', 'X')
    # Special cases for Italian
    elif language == 'it':
        s = s.replace('C\'', 'Ce ')
        s = s.replace('N\'', 'Ne ')
        s = s.replace(' c\'', ' ce ')
        s = s.replace(' n\'', ' ne ')
        s = s.replace(' v\'', ' ve ')
        s = s.replace(' quell\'', ' quelle ')
        s = s.replace(' tant\'', ' tante ')
        s = s.replace(' com\'', ' come ')

        s = s.replace(' po\'', ' poco \' ')
        s = s.replace(' di\'', ' di \' ')

        s = s.replace(' gliel\'ho', ' gliele ho ')
        s = s.replace(u' dov\'è ', u' dove è ')
    # Special cases for German
    elif language == 'de':
        s = s.replace(' bin.', ' bin .')
        s = s.replace(' uns.', ' uns .')
        s = s.replace(' geh.', ' geh .')
    # Special cases for English
    elif language == 'en':
        s = s.replace('myst\'ry', 'myst \'ry')
        s = s.replace('d\'yeh', 'do you')
        s = s.replace('D\'yeh', 'Do you')
        s = s.replace('d\'you', 'do you')
        s = s.replace('D\'you', 'Do you')
        s = s.replace('yeh\'ve', 'you have')
        s = s.replace('closer\'n', 'closer than')
        s = s.replace('More\'n', 'More than')
        s = s.replace('more\'n', 'more than')
        s = s.replace('C\'mere', 'Come here')
        s = s.replace('C\'mon', 'Come on')
        s = s.replace('o\'clock', 'of clock')
        s = s.replace('No.', 'No .')

    return s
