import os
import subprocess
import sys
import re
import stories
from urllib.request import urlretrieve
from urllib.parse import urlparse

#constants
site_prefix = 'http://www.mspaintadventures.com/'
appdir = os.path.dirname(sys.argv[0])
swix = os.path.join(appdir, 'SwiXConsole.exe')

# archiver which maintains a layout like that of mspa.com
class MirroringArchiver:
    def __init__(self, storyid, storyloc):
        self.story = storyid
        self.root = stories.dirs(self.story)[0]
        self.archdir = storyloc

        self._object_template = self._load_template('flash.txt')
        self._log_template = self._load_template('pesterlog.txt')
        self._html_template = self._load_template('page.txt')
        self._sbahj_template = self._load_template('page_sbahj.txt')
        self._scratch_template = self._load_template('page_scratch.txt')
        self._cascade_template = self._load_template('page_cascade.txt')
        self._dota_template = self._load_template('page_dota.txt')

        self._mkdir('images')
        self._get_global('images/logo.gif')
        self._get_global('images/title.png')
        self._get_global('images/v2_blankstrip.gif')
        self._get_global('images/v2_blanksquare.gif')
        self._get_global('images/v2_blanksquare2.gif')
        self._get_global('images/v2_blanksquare3.gif')
        self._get_global('images/header_cascade.gif')
        self._get_global('jquery.min.js')
        self._get_global('ddimgtooltip.css')
        self._get_global('ddimgtooltip.js')

        self._mkdir('{0}'.format(self.story))
        for directory in stories.dirs(self.story):
            self._mkdir(directory)

    def finalise(self):
        pages = filter(lambda path: path.endswith('.html'), os.listdir(str(self.story)))
        for page in pages:
            with open('{0}/{1}'.format(self.story, page), 'r') as pagefile:
                text = pagefile.read()
                text = re.sub(r'>((jb2_)?\d+)</a>', lambda match: '>{0}</a>'.format(self._page_command(match.group(1))), text)

            with open('{0}/{1}'.format(self.story, page), 'w') as pagefile:
                pagefile.write(text)

        flashes = [self.root+'/'+path for path in os.listdir(self.root) if re.match(r'\d\d\d\d\d$', path)] + ['cascade']

        for flashdir in flashes:
            for xml in filter(lambda file: file.endswith('.xml'), os.listdir(flashdir)):
                os.remove(flashdir + '/' + xml)

    #filesystem helpers
    def _load_template(self, filename):
        with open(os.path.join(appdir, 'templates', filename), 'r') as template_file:
            return template_file.read()

    def _load_binary(self, directory, filename):
        with open(os.path.join(self.archdir, directory, filename), 'rb') as f:
            return f.read()

    def _save_binary(self, directory, filename, data):
        filename = os.path.join(*filename.split('/'))
        with open(os.path.join(self.archdir, directory, filename), 'wb') as f:
            f.write(data)

    def _exists(self, directory, filename):
        return os.path.exists(os.path.join(self.archdir, directory, filename))

    def _get_global(self, filename):
        path = os.path.join(self.archdir, filename)
        if not os.path.exists(path):
            urlretrieve(site_prefix+filename, path)

    def _mkdir(self, directory):
        os.makedirs(os.path.join(self.archdir, directory), exist_ok=True)

    ### pages ###
    def save_page(self, page, data):
        self._save_binary(self.story, self._page_filename(page), data)

    def page_exists(self, page):
        return self._exists(self.story, self._page_filename(page))

    def page_load(self, page):
        return self._load_binary(self.story, self._page_filename(page))

    def _page_command(self, page):
        with open(os.path.join(self.archdir, self.story, self._page_filename(page)), 'rb') as f:
            return f.readline().decode(stories.encoding(self.story)).strip()

    def _page_filename(self, page):
        return '{0}.txt'.format(page)

    ### images ###
    def save_image(self, image, data):
        _save_binary(self.root, image, data)

    def image_exists(self, image):
        return _exists(self.root, image)

    ### flash animations ###
    def save_flash(self, flashid, script, data):
        flashdir = '{0}/{1}'.format(self.root, flashid)
        _mkdir(flashdir)
        _save_binary(flashdir, 'AC_RunActiveContent.js', script)
        _save_binary(flashdir, '{0}.swf'.format(flashid), data)
        self._flash_fix_links(flashid)

    def flash_exists(self, flashid):
        return _exists(self.root, flashid)

    def flash_load(self, flashid):
        return _load_binary('{0}/{1}'.format(self.root, flashid), '{0}.swf'.format(flashid))

    def flash_nexts(self, flashid):
        nexts = []
        xml = '{0}/{1}/{1}.xml'.format(self.root, flashid)
        swf = '{0}/{1}/{1}.swf'.format(self.root, flashid)
    
        if not os.path.exists(xml):
            with open(os.devnull, 'w') as null:
                subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

        with open(xml, 'r', encoding='utf-8') as f:
           for line in f.readlines():
                match = re.search(r'(\d\d\d\d\d\d).html', line)
                if match:
                    if int(match.group(1)) >= int(stories.first_page(self.story)):
                        nexts.append(match.group(1))
 
        return nexts

    def _flash_fix_links(self, flashid):
        xml = '{0}/{1}/{1}.xml'.format(self.root, flashid)
        swf = '{0}/{1}/{1}.swf'.format(self.root, flashid)

        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

        with open(xml, 'r') as f:
            text = f.readlines()
        text = map(self._rewrite_links, text)
        with open(xml, 'w') as f:
            f.writelines(text)

        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'xml2swf', xml, swf], stdout=null)

    def _flash_dimensions(self, flashid):
        xml = '{0}/{1}/{1}.xml'.format(self.root, flashid)
        swf = '{0}/{1}/{1}.swf'.format(self.root, flashid)

        if not os.path.exists(xml):
            with open(os.devnull, 'w') as null:
                subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

        with open(xml, 'r', encoding='utf-8') as f:
            text = f.read()
            match = re.search(r'Movie SwfVersion="\d+" Width="(\d+)" Height="(\d+)', text)
            x = match.group(1)
            y = match.group(2)

        return [x, y]

    ### misc. assets and special cases ###
    def save_misc(self, filename, data):
        if filename.endswith('/'):
            _mkdir(filename)
            _save_binary(filename, 'index.html', data)
        else:
            _save_binary('', filename, data)

    def misc_exists(self, filename):
        if filename.endswith('/'):
            return _exists(filename, 'index.html')
        else:
            return _exists('', filename)

    def misc_load(self, filename):
        if filename.endswith('/'):
            return _load_binary(filename, 'index.html')
        else:
            return _load_binary('', filename)

    def logo_path(self, remote):
        components = len(remote.split('/'))
        return '../' * (components-1) + 'images/logo.gif'

    ### [S] Cascade segments ###
    def save_cascade(self, prefix, filename, data):
        _save_binary('cascade', filename, data)

        self.cascade_prefix = prefix
        swf = 'cascade/' + filename
        xml = swf.replace('swf', 'xml')

        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

        with open(xml, 'r') as f:
            text = f.readlines()
        text = map(self._rewrite_cascade, text)
        with open(xml, 'w') as f:
            f.writelines(text)

        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'xml2swf', xml, swf], stdout=null)

    def cascade_exists(self, filename):
        return _exists('cascade', filename)

    def _rewrite_cascade(self, line):
        return re.sub(self.cascade_prefix+r'(.*)"', lambda match: '../cascade/{0}"'.format(match.group(1)), line)

    ### html output ###
    def gen_html(self, page, command, assets, content, links):
        print('>',command.encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding))
        sys.stdout.flush()

        images = map(self._format_asset, assets)
        anchors = map(self._format_anchor, links)
        content = map(self._rewrite_links, content)
        content = self._rewrite_dialogue(list(content))

        room, alt, img = stories.scratch_banner(page)
        if room:
            banner = self._format_banner(room)
            html = self._scratch_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors),
                                                 banner=banner, alt_text=alt, alt_img='imgtip[{0}]'.format(img))
        elif page == '005982':
            html = self._sbahj_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
        elif page == '006009':
            html = self._cascade_template.format(assets=self._format_cascade(), navigation=''.join(anchors), banner='../images/header_cascade.gif')
        elif page == '006715':
            html = self._dota_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
        else:
            html = self._html_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
    
        with open('{0}/{1}.html'.format(self.story, page), 'w') as f:
            f.write(html)

    def _format_banner(self, roomfile):
        return '../{0}/scratch/{1}'.format(self.root, roomfile)

    def _format_asset(self, url):
        if url.endswith('.gif') or url.endswith('.GIF'):
            return self._format_image(url)
        elif url.startswith('F|'):
            return self._format_flash(url[2:])
        else:
            raise Exception('unrecognised asset type '+url)

    def _format_image(self, asset_uri):
        return '<img src="../{0}"/>'.format(asset_uri[len(site_prefix):])

    def _format_flash(self, flash_uri):
        flashid = urlparse(flash_uri).path.split('/')[-1]

        w, h = self._flash_dimensions(flashid)

        return self._object_template.format(
            id='../{0}/{1}/{1}'.format(self.root,flashid), 
            swf='../{0}/{1}/{1}.swf'.format(self.root,flashid), 
            js='../{0}/{1}/AC_RunActiveContent.js'.format(self.root,flashid),
            width=str(w),
            height=str(h))

    def _format_cascade(self):
        return self._object_template.format(
            id='../cascade/cascade_loaderExt',
            swf='../cascade/cascade_loaderExt.swf',
            js='../cascade/AC_RunActiveContent.js',
            width='950',
            height='650')

    def _format_anchor(self, page):
        return '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page)

    def _format_internal_page(self, match):
        story = match.group(1)
        page = match.group(3)
        if page == None:
            page = '{0:06}'.format(stories.first_page(story))
        return '../{0}/{1}.html'.format(story, page)

    def _format_internal_asset(self, match):
        filename = match.group(1)
        if 'sweetbroandhellajeff' in filename:
            return '{0}{1}"'.format(site_prefix, filename)
        else:
            return '../{0}"'.format(filename)

    def _format_wv(self, match):
        vagabond = match.group(0)
        return '{0}index.html'.format(vagabond)

    def _rewrite_links(self, text):
        text = re.sub(site_prefix+r'scratch\.php\?s=(\d*)(&amp;p=(\d*))?', self._format_internal_page, text)
        text = re.sub(site_prefix+r'\?s=(\d*)(&amp;p=(\d*))?', self._format_internal_page, text)
        text = re.sub(site_prefix+r'(.*)"', self._format_internal_asset, text)
        text = re.sub(r'waywardvagabond/(.*?)/', self._format_wv, text)
        return text

    def _rewrite_dialogue(self, text):
        logtype = re.match(r'\|(.*)\|', text[0])

        if logtype != None:
            return [self._log_template.format(title=logtype.group(1).capitalize(), pesterlog='<br/>\n'.join(text[1:]))]
            
        return text
