# -*- coding: utf-8 -*-

import os
import re

from lxml import etree
from treetaggerwrapper import make_tags, NotTag

from .constants import POS_TAGS, SENT_TAGS
from .utils import eprint, instantiate_tagger


def from_xml(input_files, language, in_place=False):
    tagger = instantiate_tagger(language)

    for in_file in input_files:
        process_single(tagger, language, in_file, in_place)


def process_single(tagger, language, in_file, in_place=False):
    eprint('Now processing {}'.format(in_file))
    tree = etree.parse(in_file)
    for sentence in tree.xpath('//s'):
        # Retrieve all words in the sentence
        s = ''
        prev_word = ' '
        words = sentence.xpath('./w')
        for word in words:
            if word.text[0] in ['\'']:  # Dealing with things like "'s", and "n't"
                s += word.text
            elif language in ['fr', 'it'] and len(prev_word) > 1 and prev_word[-1] in ['\'']:  # Dealing with things like "j'ai"
                s += word.text
            else:
                s += ' ' + word.text
            prev_word = word.text

        s = apply_replacements(language, s)  # Tag/lemmatize the sentence
        tags = make_tags(tagger.tag_text(s))

        # Add the tags and lemmata back to the words
        if len(words) != len(tags):
            eprint(u'# words does not match # tags: {}'.format(s))

        for n, word in enumerate(words):
            try:
                if type(tags[n]) != NotTag:
                    word.attrib[POS_TAGS.get(language, 'tree')] = tags[n].pos
                    word.attrib['lem'] = tags[n].lemma
            except IndexError:
                # The end of a sentence is sometimes not properly recognized, deal as a special case.
                if word.text == '.':
                    eprint(u'End of sentence reached: {}'.format(s))
                    word.attrib[POS_TAGS.get(language, 'tree')] = SENT_TAGS.get(language, 'SENT')
                    word.attrib['lem'] = '.'
                # Otherwise, print the sentence
                else:
                    eprint(u'IndexError: {}'.format(s))

    # Output the result to a file
    if in_place:
        out_file = in_file
    else:
        out_file, ext = os.path.splitext(in_file)
        out_file += '-out' + ext

    tree.write(out_file, pretty_print=True, xml_declaration=True, encoding='utf-8')


def apply_replacements(language, s):
    # Special cases for Dutch
    if language == 'nl':
        s = re.sub(r'(Meneer\s\w)\.', r'\1', s, flags=re.IGNORECASE)
        s = re.sub(r'(Heer\s\w)\.', r'\1', s, flags=re.IGNORECASE)
        s = re.sub(r'(Mevrouw\s\w)\.', r'\1', s, flags=re.IGNORECASE)
        s = re.sub(r'(Prof(?:essor|\.)?\s\w)\.', r'\1', s, flags=re.IGNORECASE)

        s = re.sub(r'\'s\s(ochtends)', r' des \1', s, flags=re.IGNORECASE)  # 's ochtends
        s = re.sub(r'\'s\s(middags)', r' des \1', s, flags=re.IGNORECASE)  # 's middags
        s = re.sub(r'\'s\s(avonds)', r' des \1', s, flags=re.IGNORECASE)  # 's avonds
        s = re.sub(r'\'s\s(nachts)', r' des \1', s, flags=re.IGNORECASE)  # 's nachts

        s = s.replace('\'t', ' het')
        s = s.replace('\'m', ' hem')

        s = s.replace('9 3/4', '9 34')  # The platform number isn't processed correctly
    # Special cases for French
    elif language == 'fr':
        s = s.replace('Aujourd\'hui', 'Jour hui')
        s = s.replace('aujourd\'hui', 'jour hui')

        s = s.replace(u'd\'après', u'de après')
        s = s.replace(u'D\'après', u'De après')

        s = s.replace(u'C\'est-à-dire', u'Ce est-à-dire')
        s = s.replace(u'c\'est-à-dire', u'ce est-à-dire')

        s = re.sub('(d)\'abord', r'\1e abord', s, flags=re.IGNORECASE)
        s = re.sub('(d)\'accord', r'\1e accord', s, flags=re.IGNORECASE)
        s = re.sub('(d)\'ailleurs', r'\1e ailleurs', s, flags=re.IGNORECASE)
        s = re.sub('(d)\'autant', r'\1e autant', s, flags=re.IGNORECASE)
        s = re.sub(r'(quelqu)\'un', r'\1e un', s, flags=re.IGNORECASE)
        s = re.sub(r'(va)-t\'en', r'\1-te en', s, flags=re.IGNORECASE)

        s = s.replace(u'-là', u'')
        s = s.replace(u'-mêmes', u'')
        s = s.replace(u'-même', u'')
        s = re.sub(r'(\w+)-(je|moi|tu|toi|t-il|il|lui|la|les|vous|ce|ci|y|en)', r'\1', s, flags=re.IGNORECASE)

        s = s.replace('M.', 'Mr')
        s = s.replace('X.', 'X')
    # Special cases for Italian
    elif language == 'it':
        s = s.replace(u'\'è', u'e è')
        s = re.sub(r'\'([eaihou])', r'e \1', s, flags=re.IGNORECASE)

        s = re.sub(r'(Mrs?\s\w)\.', r'\1', s, flags=re.IGNORECASE)
    # Special cases for German
    elif language == 'de':
        s = s.replace(' bin.', ' bin .')
        s = s.replace(' uns.', ' uns .')
        s = s.replace(' geh.', ' geh .')
        s = s.replace(' komm.', ' komm .')
    elif language == 'es':
        s = re.sub(r'(Señora?\s\w)\.', r'\1', s, flags=re.IGNORECASE)
        s = re.sub(r'(Prof(?:essor|\.)?\s\w)\.', r'\1', s, flags=re.IGNORECASE)
    # Special cases for English
    elif language == 'en':
        # Titles
        s = re.sub(r'(Mrs?\s\w)\.', r'\1', s, flags=re.IGNORECASE)
        s = re.sub(r'(Prof(?:essor|\.)?\s\w)\.', r'\1', s, flags=re.IGNORECASE)

        s = s.replace('No.', 'No .')
        s = s.replace('o\'clock', 'of clock')
        s = s.replace('what\'s-her-name', 'what is-her-name')

        # Below are utterances by Hagrid, so even more special cases
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
        s = s.replace('good\'un', 'good one')
        s = re.sub(r'(should)n\'ta', r'\1nt have', s, flags=re.IGNORECASE)

    return s
