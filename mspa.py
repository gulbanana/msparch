from urllib.request import urlopen
from urllib.parse import urlparse
from itertools import *
from asq.initiators import query
import re
import archive

# site-related constants
site_prefix = 'http://www.mspaintadventures.com/'

# parse a page's description file
def _separated_sections(iterable):
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

# main reader class which pulls from the web
class SiteReader:
    def __init__(self, storyid, archiveimpl):
        self.story = storyid
        self.archiver = archiveimpl

    # retrieve one page
    def get_page(self, page):
        if self.archiver.page_exists(page):
            definition = self.archiver.load_page(page)
        else:
            page_uri = site_prefix + '{0}/{1}.txt'.format(self.story, page)
            definition = urlopen(page_uri).readall()
            self.archiver.save_page(page, definition)

        command, hash1, hash2, art, narration, next_pages = _separated_sections(definition.splitlines())

        for line in art:
           self.__get_asset(line) 

        for line in narration:
            for match in re.findall(site_prefix+r'([^\?]*?)"', line):
                self.__get_asset(site_prefix+match)

        self.archiver.gen_html(page, command[0], art, narration, next_pages)

        return next_pages

    # retrieve an non-page asset 
    def __get_asset(self, uri):
        if uri.startswith('F|'):
            self.__get_flash(uri[2:])
        elif uri.endswith('YOUWIN.gif'):
            self.__get_other(uri)
        elif uri.endswith('.gif') or uri.endswith('.GIF') or uri.endswith('.jpg'):
            self.__get_image(uri)
        elif re.search(r'extras.*html', uri):
            self.__get_donation_command(uri)
        else:
            raise Exception('asset type {0} not supported'.format(uri))
    
    # retrieve an image file
    def __get_image(self, uri):
        # special case: jailbreak can have multi-level paths
        if re.search('jb/', uri):
            filename = urlparse(uri).path.split('jb/')[-1]
        else:
            filename = urlparse(uri).path.split('/')[-1]

        if not self.archiver.image_exists(filename):
            data = urlopen(uri).readall()
            self.archiver.save_image(filename, data)

    # retrieve a flash animation
    def __get_flash(self, uri):
        flashid = urlparse(uri).path.split('/')[-1]

        if not self.archiver.flash_exists(flashid):
            js = urlopen(uri + '/AC_RunActiveContent.js').readall()
            swf = urlopen('{0}/{1}.swf'.format(uri, flashid)).readall()
            self.archiver.save_flash(flashid, js, swf)

    # retrieve any type of file
    def __get_other(self, uri):
        filename = urlparse(uri).path[1:]

        if not self.archiver.misc_exists(filename):
            data = urlopen(uri).readall()
            self.archiver.save_misc(filename, data)

    # retrieve a problem sleuth donation command
    def __get_donation_command(self, uri):
        html = urlopen(uri).readall().decode('iso8859-1')

        for img in re.findall(r'src="({0}.*?)"'.format(site_prefix), html):
            if not re.search(r'logo', img):
                self.__get_other(img)
            imgfilename = urlparse(img).path[1:]
    
        html = re.sub(r'src="{0}(.*?)"'.format(site_prefix), r'src="../\1"', html)
        
        filename = urlparse(uri).path[1:]
        if not self.archiver.misc_exists(filename):
            self.archiver.save_misc(filename, html.encode('iso8859-1'))

