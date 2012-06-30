import os
import sys
import re
import stories
from urllib.request import urlretrieve
from urllib.parse import urlparse

#constants
site_prefix = 'http://www.mspaintadventures.com/'


class MirroringArchiver:
    def __init__(self, storyid):
        self.story = storyid
        self.root = stories.dirs(self.story)[0]

        with open('templates/page.txt', 'r') as template_file:
            self._html_template = template_file.read()
        with open('templates/flash.txt', 'r') as template_file:
            self._object_template = template_file.read()

        os.makedirs('images', exist_ok=True)
        self.__get_global('images/logo.gif')
        self.__get_global('images/title.png')

        os.makedirs('{0}'.format(self.story), exist_ok=True)
        for directory in stories.dirs(self.story):
            os.makedirs(directory, exist_ok=True)

    def __get_global(self, filename):
        if not os.path.exists(filename):
            urlretrieve(site_prefix+filename, filename)

    def finalise(self):
        pages = filter(lambda path: path.endswith('.html'), os.listdir(str(self.story)))

        for page in pages:
            with open('{0}/{1}'.format(self.story, page), 'r') as pagefile:
                text = pagefile.read()
                text = re.sub(r'>((jb2_)?\d*)</a>', lambda match: '>{0}</a>'.format(self.__page_command(match.group(1))), text)

            with open('{0}/{1}'.format(self.story, page), 'w') as pagefile:
                pagefile.write(text)

    ### pages ###
    def save_page(self, page, data):
        with open('{0}/{1}.txt'.format(self.story, page), 'wb') as f:
            f.write(data)

    def page_exists(self, page):
        return os.path.exists('{0}/{1}.txt'.format(self.story, page))

    def load_page(self, page):
        with open('{0}/{1}.txt'.format(self.story, page), 'rb') as f:
            return f.read()

    def __page_command(self, page):
        with open('{0}/{1}.txt'.format(self.story, page), 'r') as f:
            return f.readline().strip()

    ### images ###
    def save_image(self, image, data):
        with open('{0}/{1}'.format(self.root, image), 'wb') as f:
            f.write(data)

    def image_exists(self, image):
        return os.path.exists('{0}/{1}'.format(self.root, image))

    ### flash animations ###
    def save_flash(self, flashid, script, flash):
        os.makedirs('{0}/{1}'.format(self.root, flashid), exist_ok=False)
    
        with open('{0}/{1}/AC_RunActiveContent.js'.format(self.root, flashid), 'wb') as script_file:
            script_file.write(script)

        with open('{0}/{1}/{1}.swf'.format(self.root, flashid), 'wb') as flash_file:
            flash_file.write(flash)

    def flash_exists(self, flashid):
        return os.path.exists('{0}/{1}'.format(self.root, flashid))

    ### misc. assets and special cases ###
    def save_misc(self, filename, data):
        with open(filename, 'wb') as f:
            f.write(data)

    def misc_exists(self, filename):
        return os.path.exists(filename)

    def load_misc(self, filename):
        with open(filename, 'rb') as f:
            return f.read()

    ### html output ###
    def gen_html(self, page, command, assets, content, links):
        print('>',command)
        sys.stdout.flush()

        images = map(self.__format_asset, assets)
        anchors = map(self.__format_anchor, links)
        content = map(self.__rewrite_links, content)
        content = self.__rewrite_dialogue(content)

        html = self._html_template.format(command=command, assets='<br><br>'.join(images), narration='<br>'.join(content), navigation=''.join(anchors))
    
        with open('{0}/{1}.html'.format(self.story, page), 'w') as f:
            f.write(html)

    def __format_asset(self, url):
        if url.endswith('.gif') or url.endswith('.GIF'):
            return self.__format_image(url)
        elif url.startswith('F|'):
            return self.__format_flash(url[2:])
        else:
            raise Exception('unrecognised asset type '+url)

    def __format_image(self, asset_uri):
        return '<img src="../{0}"/>'.format(asset_uri[len(site_prefix):])

    def __format_flash(self, flash_uri):
        flashid = urlparse(flash_uri).path.split('/')[-1]
        return self._object_template.format(
            id='../{0}/{1}/{1}'.format(self.root,flashid), 
            swf='../{0}/{1}/{1}.swf'.format(self.root,flashid), 
            js='../{0}/{1}/AC_RunActiveContent.js'.format(self.root,flashid))

    def __format_anchor(self, page):
        return '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page)

    def __format_internal_page(self, match):
        story = match.group(1)
        page = match.group(3)
        if page == None:
            page = '{0:06}'.format(stories.first_page(story))
        return '../{0}/{1}.html'.format(story, page)

    def __format_internal_image(self, match):
        filename = match.group(1)
        return '../{0}"'.format(filename)

    def __rewrite_links(self, text):
        text = re.sub(site_prefix+r'\?s=(\d*)(&amp;p=(\d*))?', self.__format_internal_page, text)
        text = re.sub(site_prefix+r'(.*)"', self.__format_internal_image, text)
        return text

    def __rewrite_dialogue(self, text):
        return text
