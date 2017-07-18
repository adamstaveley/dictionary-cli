# dictionary-cli

Search for infomation about words from the command line. 

```
usage: dictionary.py [-h] [-d] [-t] [-p] [-eg] [-fr] <phrase>

positional arguments [required]:
  phrase

optional arguments:
  -h, --help  show this help message and exit
  -d          only show definition
  -t          search thesaurus
  -p          play pronunciation
  -eg         show example sentance
  -fr         show French translation
```

Notes:
* requires Python 3.6 due to use of f-strings
* additional Python modules required are provided in requirements.txt and
    can be installed using `pip install -r requirements.txt`
* mpv and youtube-dl are required to play pronunciation snippets
