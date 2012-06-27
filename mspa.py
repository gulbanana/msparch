from urllib.request import urlopen
from urllib.parse import urlparse
from itertools import *
import re
import archive

site_prefix = 'http://www.mspaintadventures.com/'
def definition_uri(story, page):
    return site_prefix + '{0}/{1}.txt'.format(story, page)

def separated_sections(iterable):
    sections = []
    accumulator = []

    for line in iterable:
        # file terminator - X = one choice ? = multiple choice O = end of bard quest
        if line == b'X' or line == b'?' or line == b'O':
            sections.append(accumulator)
            return sections

        # section terminator
        elif line == b'###':
            sections.append(accumulator)
            accumulator = []

        # line within section
        else:
            accumulator.append(line.decode())

def get_page(story, page):
    if archive.page_exists(story, page):
        return []

    definition = urlopen(definition_uri(story, page)).readall()

    command, hash1, hash2, art, narration, next_pages = separated_sections(definition.splitlines())

    for line in art:
       get_asset(story, line) 

    archive.gen_html(story, page, command[0], art, narration, next_pages)
    archive.save_page(story, page, definition)

    return next_pages

def get_asset(story, uri):
    if uri.endswith('.gif'):
        get_image(story, uri)
    elif uri.endswith('.GIF'):
        get_image(story, uri)
    else:
        raise Exception('asset type ' + uri + ' not yet supported')
    
def get_image(story, uri):
    # special case: jailbreak can have multi-level paths
    if re.search('jb/', uri):
        filename = urlparse(uri).path.split('jb/')[-1]
    else:
        filename = urlparse(uri).path.split('/')[-1]

    print(filename)
    data = urlopen(uri).readall()

    archive.save_image(story, filename, data)
