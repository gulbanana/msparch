from urllib.request import urlopen
from urllib.parse import urlparse
from itertools import *
from asq.initiators import query
import re
import archive

def definition_uri(story, page):
    return archive.site_prefix + '{0}/{1}.txt'.format(story, page)

# parse a page's description file
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
            accumulator.append(line.decode('iso8859-1'))

# retrieve one page
def get_page(story, page):
    if archive.page_exists(story, page):
        definition = archive.load_page(story, page)
    else:
        definition = urlopen(definition_uri(story, page)).readall()
        archive.save_page(story, page, definition)

    command, hash1, hash2, art, narration, next_pages = separated_sections(definition.splitlines())

    for line in art:
       get_asset(story, line) 

    for line in narration:
        for match in re.findall(archive.site_prefix+r'([^\?]*?)"', line):
            get_asset(story, archive.site_prefix+match)

    archive.gen_html(story, page, command[0], art, narration, next_pages)

    return next_pages

# retrieve an non-page asset 
def get_asset(story, uri):
    if uri.endswith('YOUWIN.gif'):
        get_other(story, uri)

    elif uri.endswith('.gif') or uri.endswith('.GIF'):
        get_image(story, uri)

    elif re.search(r'extras.*html', uri):
        get_donation_command(story, uri)
        
    else:
        raise Exception('asset type {0} not supported'.format(uri))
    
# retrieve an image file
def get_image(story, uri):
    # special case: jailbreak can have multi-level paths
    if re.search('jb/', uri):
        filename = urlparse(uri).path.split('jb/')[-1]
    else:
        filename = urlparse(uri).path.split('/')[-1]

    if not archive.image_exists(story, filename):
        data = urlopen(uri).readall()
        archive.save_image(story, filename, data)

# retrieve any type of file
def get_other(story, uri):
    filename = uri[len(archive.site_prefix):]

    if not archive.misc_exists(story, filename):
        data = urlopen(uri).readall()
        archive.save_misc(story, filename, data)

# retrieve a problem sleuth donation command
def get_donation_command(story, uri):
    html = urlopen(uri).readall().decode('iso8859-1')

    for img in re.findall(r'src="({0}.*?)"'.format(archive.site_prefix), html):
        if not re.search(r'logo', img):
            get_other(story, img)
        imgfilename = img[len(archive.site_prefix):]
    
    html = re.sub(r'src="{0}(.*?)"'.format(archive.site_prefix), r'src="../\1"', html)
        
    filename = uri[len(archive.site_prefix):]
    if not archive.misc_exists(story, filename):
        archive.save_misc(story, filename, html.encode('iso8859-1'))

