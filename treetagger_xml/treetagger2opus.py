# -*- coding: utf-8 -*-

import argparse
import codecs

from lxml import etree


def process(file_in, file_out, sentence_tokenized=False):
    with codecs.open(file_in, 'r', encoding='utf-8') as f:
        text = etree.Element('text')

        i = j = k = 0
        paragraph_start = sentence_start = True
        end_after_next = False

        lines = f.readlines()
        for n, line in enumerate(lines):
            line = line.strip()

            if not line:
                if sentence_tokenized and not sentence_start:
                    sentence_start = True
                else:
                    paragraph_start = True
                continue

            if paragraph_start:
                i += 1
                j = 0
                paragraph = etree.SubElement(text, 'p')
                paragraph.set('id', str(i))
                paragraph_start = False
                sentence_start = True

            if sentence_start:
                j += 1
                k = 0
                sentence = etree.SubElement(paragraph, 's')
                sentence.set('id', 's{}.{}'.format(i, j))
                sentence_start = False

            w, tag, lemma = split_line(line, n)

            k += 1
            word = etree.SubElement(sentence, 'w')
            word.set('id', 'w{}.{}.{}'.format(i, j, k))
            word.text = w
            if tag:
                word.set('tree', tag)
            if lemma:
                word.set('lem', lemma)

            if end_after_next:
                sentence_start = True
                end_after_next = False

            # The 'SENT' marks a sentence end in Greek, Z.Fst, Z.Int, Z.Exc for Estonian,
            # PUNCT.Final for Catalan, Fp for Portuguese
            if not sentence_tokenized and tag in ['SENT', 'Z.Fst', 'Z.Int', 'Z.Exc', 'PUNCT.Final', 'Fp']:
                # Peek forward if we're not dealing with a dialogue
                if lines[n+1]:
                    _, next_tag, _ = split_line(lines[n+1], n+1)
                    if next_tag in ['Z.Quo'] or (lemma != ':' and next_tag in ['PUNCT']):
                        end_after_next = True
                    else:
                        sentence_start = True
                else:
                    sentence_start = True

        tree = etree.ElementTree(text)
        tree.write(file_out, pretty_print=True, xml_declaration=True, encoding='utf-8')


def split_line(line, n):
    # Split into word, tag and lemma (or word and tag if this line only contains two values)
    line_split = line.split('\t')

    if 1 <= len(line_split) <= 3:
        w = line_split[0]
        tag = ''
        lemma = ''

        if len(line_split) >= 2:
            tag = line_split[1]

            if len(line_split) >= 3:
                lemma = line_split[2]
    else:
        raise ValueError('Incorrect at line {}'.format(n))

    return w, tag, lemma


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file_in', help='Input file')
    parser.add_argument('file_out', help='Output file')
    parser.add_argument('--tok', action='store_true', help='Is the file sentence-tokenized?')
    args = parser.parse_args()

    process(args.file_in, args.file_out, args.tok)
