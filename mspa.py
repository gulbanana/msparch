from urllib.request import urlopen
from urllib.parse import urlparse
from itertools import *
from asq.initiators import query
import re
import archive
import stories

# site-related constants
site_prefix = r'http://www.mspaintadventures.com/'
site_logo = r'http://www.mspaintadventures.com/images/logo.gif'

# main reader class which pulls from the web
class SiteReader:
    def __init__(self, storyid, archiveimpl):
        self.story = storyid
        self.archiver = archiveimpl

    # parse a page's description file
    def _separated_sections(self, iterable):
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
                accumulator.append(line.decode(stories.encoding(self.story)))

    # retrieve one page
    def get_page(self, page):
        if self.archiver.page_exists(page):
            definition = self.archiver.page_load(page)
        else:
            page_uri = site_prefix + '{0}/{1}.txt'.format(self.story, page)
            definition = urlopen(page_uri).readall()
            self.archiver.save_page(page, definition)

        if page == '006009':
            return self._get_cascade()

        command, hash1, hash2, art, narration, next_pages = self._separated_sections(definition.splitlines())

        # banner
        room = stories.scratch_banner(page)
        if room:
            self._get_asset(site_prefix+'storyfiles/hs2/scratch/'+room)

        # main images
        hidden_nexts = []
        for line in art:
            hidden_nexts.extend(self._get_asset(line))

        # inline images
        for line in narration:
            for match in re.findall(site_prefix+r'([^\?]*?)"', line):
                if not 'sweetbroandhellajeff' in match:
                    self._get_asset(site_prefix+match)

        self.archiver.gen_html(page, command[0], art, narration, next_pages)

        return map(lambda s: s.strip(), next_pages + hidden_nexts)

    # retrieve an non-page asset. this can trigger additional page loads 
    def _get_asset(self, uri):
        if uri.startswith('F|'):
            return self._get_flash(uri[2:])
        elif 'scraps' in uri or 'jb2' in uri or 'scratch' in uri:
            self._get_other(uri)
        elif uri.endswith('.gif') or uri.endswith('.GIF') or uri.endswith('.jpg'):
            self._get_image(uri)
        elif re.search(r'extras.*html', uri) or 'waywardvagabond' in uri:
            self._get_standalone(uri)
        else:
            raise Exception('asset type {0} not supported'.format(uri))
        return []
    
    # retrieve an image file
    def _get_image(self, uri):
        # special case: jailbreak can have multi-level paths
        if 'jb/' in uri:
            filename = urlparse(uri).path.split('jb/')[-1]
        else:
            filename = urlparse(uri).path.split('/')[-1]

        if not self.archiver.image_exists(filename):
            data = urlopen(uri).readall()
            self.archiver.save_image(filename, data)

    # retrieve a flash animation
    def _get_flash(self, uri):
        flashid = urlparse(uri).path.split('/')[-1]

        if not self.archiver.flash_exists(flashid):
            js = urlopen(uri + '/AC_RunActiveContent.js').readall()
            swf = urlopen('{0}/{1}.swf'.format(uri, flashid)).readall()
            self.archiver.save_flash(flashid, js, swf)

        # additional nexts
        return self.archiver.flash_nexts(flashid)

    # retrieve any type of file
    def _get_other(self, uri):
        filename = urlparse(uri).path[1:]

        if not self.archiver.misc_exists(filename):
            data = urlopen(uri).readall()
            self.archiver.save_misc(filename, data)

    # retrieve an independent page with its own images and html
    def _get_standalone(self, uri):
        filename = urlparse(uri).path[1:]
        if self.archiver.misc_exists(filename):
            data = self.archiver.misc_load(filename)
        else:
            data = urlopen(uri).readall()

        html = data.decode('iso8859-1')

        modhtml = re.sub(site_logo, self.archiver.logo_path(filename), html)
        modhtml = re.sub(r'src="{0}(.*?)"'.format(site_prefix), r'src="../\1"', modhtml)
        
        self.archiver.save_misc(filename, modhtml.encode('iso8859-1'))

        for img in re.findall(r'src="(.*?)"', html):
            if 'logo' in img:    # site logo
                pass
            elif '..' in img:  # donation command images
                self._get_other('{0}{1}'.format(site_prefix, img[3:]))
            else:                          # wayward vagabond images
                self._get_other('{0}{1}'.format(uri, img))

    def _get_cascade(self):
        prefix = 'http://uploads.ungrounded.net/userassets/3591000/3591093/' #alternatively: site_prefix/cascade/
        files = ['cascade_loaderExt.swf', 'cascade_segment1.swf', 'cascade_segment2.swf', 'cascade_segment3.swf', 'cascade_segment4.swf', 'cascade_segment5.swf']

        self._get_other(site_prefix + 'cascade/AC_RunActiveContent.js')

        for filename in filter(lambda segment: not self.archiver.cascade_exists(segment), files):
            uri = prefix + filename
            data = urlopen(uri).readall()
            self.archiver.save_cascade(prefix, filename, data)

        self.archiver.gen_html('006009', '[S] Cascade', [], [''], ['006010'])

        return ['006010']
