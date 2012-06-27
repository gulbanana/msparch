from urllib.request import urlopen
from urllib.parse import urlparse
from itertools import *
import archive
import sys

site_prefix = 'http://www.mspaintadventures.com/'
def definition_uri(story, page):
    return site_prefix + '{0}/{1:06}.txt'.format(story, page)

def separated_sections(iterable):
    sections = []
    accumulator = []

    for line in iterable:
        if line == b'X':
            sections.append(accumulator)
            return sections
        elif line == b'###':
            sections.append(accumulator)
            accumulator = []
        else:
            accumulator.append(line.decode())

def get_page(story, page):
    definition = urlopen(definition_uri(story, page)).readall()
    archive.save_page(story, page, definition)

    # parse the definition file into its components
    command, hash1, hash2, art, narration, next_pages = separated_sections(definition.splitlines())

    # command at top of page
    print('==>',command[0])
    sys.stdout.flush()

    # one or more pieces of art
    for line in art:
       get_asset(story, line) 

    return map(lambda s: int(s), next_pages)

def get_asset(story, uri):
    if uri.endswith('.gif'):
        get_image(story, uri)
    else:
        raise Exception('asset type ' + uri + ' not yet supported')
    
def get_image(story, uri):
    filename = urlparse(uri).path.split('/')[-1]
    data = urlopen(uri).readall()

    archive.save_image(story, filename, data)
