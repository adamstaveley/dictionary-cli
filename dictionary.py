#!/usr/bin/python3

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
    add('-fr', dest='french', action='store_true', help='show French translation')
    add('-de', dest='german', action='store_true', help='show German translation')
    add('phrase', nargs=argparse.REMAINDER)
    return parser.parse_args()


class Dictionary:
    def __init__(self, phrase):
        if not phrase:
            raise Exception('No phrase given')
        else:
            self.phrase = phrase[0]

        self.dict_api = f'http://api.pearson.com/v2/dictionaries/ldoce5/entries?headword={self.phrase}'
        self.fr_api = f'https://glosbe.com/gapi/translate?from=eng&dest=fra&phrase={self.phrase}&format=json'
        self.de_api = self.fr_api.replace('dest=fra', 'dest=deu')
        self.thesaurus_api = f'http://www.thesaurus.com/browse/{self.phrase}'

    def all(self):
        results = [
            self.define(),
            # self.thesaurus(),
            self.translate(fr=True),
            self.translate(de=True)
        ]
        return '\n'.join(results)

    def define(self, pronounce=False):
        res = requests.get(self.dict_api).json()
        if not res.get('status') == 200:
            raise Exception('Definition not found')
        definition = res['results'][0]['senses'][0]['definition'][0]
        ipa = res['results'][0]['pronunciations'][0]['ipa']
        if pronounce:
            path = res['results'][0]['pronunciations'][0]['audio'][0]['url']
            filename = path.split('/')[-1]
            url = f'http://www.ldoceonline.com/media/english/breProns/{filename}'
            subprocess.run(['mpv', '--vid=no', url])
        else:
            return f'{self.phrase} [{ipa}]: {definition}'

    def thesaurus(self):
        res = requests.get(self.thesaurus_api).text
        html = bs4.BeautifulSoup(res, 'html.parser')
        synonym_list = html.select('#filters-0 .relevancy-list')[0]
        raw_synonyms = synonym_list.select('span.text')
        synonyms = [s.getText() for s in raw_synonyms]
        return 'synonyms: ' + ', '.join(synonyms)

    def translate(self, fr=False, de=False):
        prefix = '[fr]' if fr else '[de]' if de else None
        url = self.fr_api if fr else self.de_api if de else None
        if url:
            res = requests.get(url).json()
            if res.get('result') == 'ok':
                translation = res['tuc'][0]['phrase']['text']
                return f'{prefix} {translation}'
            else:
                raise Exception('Unable to translate')


def main():
    options = parse_options()
    try:
        d = Dictionary(options.phrase)
        if options.definition:
            output = d.define()
        elif options.thesaurus:
            output = d.thesaurus()
        elif options.pronounce:
            d.define(pronounce=True)
            output = None
        elif options.french or options.german:
            output = d.translate(fr=options.french, de=options.german)
        else:
            output = d.all()
    except Exception as err:
        print(err)
    else:
        print(output)


if '__main__' in __name__:
    main()
