#!/usr/bin/python3

import sys
import argparse
import subprocess
import requests
import bs4


def parse_options():
    parser = argparse.ArgumentParser()
    add = parser.add_argument
    add('-d', dest='definition', action='store_true', help='only show definition')
    add('-t', dest='thesaurus', action='store_true', help='search thesaurus')
    add('-p', dest='pronounce', action='store_true', help='play pronunciation')
    add('-eg', dest='example', action='store_true', help='show example sentance')
    add('-fr', dest='french', action='store_true', help='show French translation')
    add('phrase', nargs=argparse.REMAINDER)
    return parser.parse_args()


class Dictionary:
    def __init__(self, phrase):
        if not phrase:
            raise Exception('No phrase given')
        else:
            self.phrase = phrase[0]

        self.dict_api = f'http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword={self.phrase}'
        self.translate_api = f'https://glosbe.com/gapi/translate?from=eng&dest=fra&phrase={self.phrase}&format=json'
        self.thesaurus_api = f'http://www.thesaurus.com/browse/{self.phrase}'

    def all(self):
        results = [self.define(), self.thesaurus(), self.translate()]
        return '\n\n'.join(results)

    def define(self, mode=None):
        res = requests.get(self.dict_api).json()
        if not res.get('status') == 200:
            raise Exception('Definition not found')
        definition = res['results'][0]['senses'][0]['definition'][0]
        ipa = res['results'][0]['pronunciations'][0]['ipa']
        eg = self.find_example(res['results'][0]['senses'][0])
        if mode:
            if mode == 'example':
                return f'e.g. {eg}'
            elif mode == 'pronounce':
                path = res['results'][0]['pronunciations'][0]['audio'][0]['url']
                filename = path.split('/')[-1]
                url = f'http://www.ldoceonline.com/media/english/breProns/{filename}'
                subprocess.run(['mpv', '--vid=no', url])
        else:
            return f'{self.phrase} [{ipa}]: {definition}\n\ne.g. {eg}'

    
    def find_example(self, res):
        try:
            eg = res['collocation_examples'][0]['example']['text']
        except KeyError:
            eg = res['examples'][0]['text']
        finally:
            return eg
            
    def thesaurus(self):
        res = requests.get(self.thesaurus_api).text
        html = bs4.BeautifulSoup(res, 'html.parser')
        synonym_list = html.select('#filters-0 .relevancy-list')[0]
        raw_synonyms = synonym_list.select('span.text')
        synonyms = [s.getText() for s in raw_synonyms]
        return 'synonyms: ' + ', '.join(synonyms)

    def translate(self):
        res = requests.get(self.translate_api).json()
        if res.get('result') == 'ok':
            fr = res['tuc'][0]['phrase']['text']
            return f'[fr] {fr}'
        else:
            raise Exception('Unable to translate')


def run_dictionary():
    options = parse_options()
    try:
        d = Dictionary(options.phrase)
        if options.definition:
            output = d.define()
        elif options.thesaurus:
            output = d.thesaurus()
        elif options.example:
            output = d.define(mode='example')
        elif options.pronounce:
            d.define(mode='pronounce')
            output = None
        elif options.french:
            output = d.translate()
        else:
            output = d.all()
    except Exception as err:
        print(err)
    else:
        print(output)


if '__main__' in __name__:
    run_dictionary()
