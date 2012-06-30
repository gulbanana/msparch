import os
import sys
import re
from urllib.request import urlretrieve
from urllib.parse import urlparse

#constants
site_prefix = 'http://www.mspaintadventures.com/'

with open('templates/page.txt', 'r') as template_file:
    _html_template = template_file.read()
with open('templates/flash.txt', 'r') as template_file:
    _object_template = template_file.read()

### stories ###
def initialise(story):
    os.makedirs('images', exist_ok=True)
    _get_global('images/logo.gif')
    _get_global('images/title.png')

    os.makedirs('{0}'.format(story), exist_ok=True)
    for directory in _story_dirs(story):
        os.makedirs(directory, exist_ok=True)

def _get_global(filename):
    if not os.path.exists(filename):
        urlretrieve(site_prefix+filename, filename)

def finalise(story):
    pages = filter(lambda path: path.endswith('.html'), os.listdir(str(story)))
    for page in pages:
        with open('{0}/{1}'.format(story, page), 'r') as pagefile:
            text = pagefile.read()

        text = re.sub(r'>((jb2_)?\d*)</a>', lambda match: '>{0}</a>'.format(_page_command(story, match.group(1))), text)

        with open('{0}/{1}'.format(story, page), 'w') as pagefile:
            pagefile.write(text)

def first_page(story):
    if story == '1':
        return 2
    elif story == '2':
        return 136
    elif story == '4':
        return 219
    elif story == '5':
        return 1893
    elif story == '6':
        return 1901
    elif story == 'ryanquest':
        return 1
    else:
        raise Exception('story id {0} not supported'.format(story))

def _story_dirs(story):
    if story == '1':
        return ['advimgs/jb', 'advimgs/jb/lv2_option1', 'advimgs/jb/lv2_option2', 'advimgs/jb/lv3', 'advimgs/jb/lv4', 'storyfiles/jb2']
    elif story == '2':
        return ['advimgs/bq']
    elif story == '4':
        return ['advimgs/ps', 'extras']
    elif story == '5':
        return ['storyfiles/hs']
    elif story == '6':
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps']
    elif story == 'ryanquest':
        return ['ryanquest']
    else:
        raise Exception('story id {0} unknown'.format(story))

### pages ###
def save_page(story, page, data):
    with open('{0}/{1}.txt'.format(story, page), 'wb') as f:
        f.write(data)

def page_exists(story, page):
    return os.path.exists('{0}/{1}.txt'.format(story, page))

def load_page(story, page):
    with open('{0}/{1}.txt'.format(story, page), 'rb') as f:
        return f.read()

def _page_command(story, page):
    with open('{0}/{1}.txt'.format(story, page), 'r') as f:
        return f.readline().strip()


### images ###
def save_image(story, image, data):
    with open('{0}/{1}'.format(_story_dirs(story)[0], image), 'wb') as f:
        f.write(data)

def image_exists(story, image):
    return os.path.exists('{0}/{1}'.format(_story_dirs(story)[0], image))

### flash animations ###
def save_flash(story, flashid, script, flash):
    root = _story_dirs(story)[0]

    os.makedirs('{0}/{1}'.format(root, flashid), exist_ok=False)
    
    with open('{0}/{1}/AC_RunActiveContent.js'.format(root, flashid), 'wb') as script_file:
        script_file.write(script)

    with open('{0}/{1}/{1}.swf'.format(root, flashid), 'wb') as flash_file:
        flash_file.write(flash)

def flash_exists(story, flashid):
    root = _story_dirs(story)[0]
    return os.path.exists('{0}/{1}'.format(root, flashid))

### misc. assets and special cases ###
def save_misc(story, filename, data):
    with open(filename, 'wb') as f:
        f.write(data)

def misc_exists(story, filename):
    return os.path.exists(filename)

def load_misc(story, filename):
    with open(filename, 'rb') as f:
        return f.read()

### html output ###
def gen_html(story, page, command, assets, content, links):
    print('>',command)
    sys.stdout.flush()

    images = map(_format_asset, assets)

    anchors = map(_format_anchor, links)

    content = map(_rewrite_links, content)
    content = _rewrite_dialogue(content)

    html = _html_template.format(command=command, assets='<br><br>'.join(images), narration='<br>'.join(content), navigation=''.join(anchors))
    
    with open('{0}/{1}.html'.format(story, page), 'w') as f:
        f.write(html)

def _format_asset(url):
    if url.endswith('.gif') or url.endswith('.GIF'):
        return _format_image(url)
    elif url.startswith('F|'):
        return _format_flash(url[2:])
    else:
        raise Exception('unrecognised asset type '+url)

def _format_image(asset_uri):
    return '<img src="../{0}"/>'.format(asset_uri[len(site_prefix):])

def _format_flash(flash_uri):
    flashid = urlparse(flash_uri).path.split('/')[-1]
    root = _story_dirs('5')[0]

    return _object_template.format(
        id='../{0}/{1}/{1}'.format(root,flashid), 
        swf='../{0}/{1}/{1}.swf'.format(root,flashid), 
        js='../{0}/{1}/AC_RunActiveContent.js'.format(root,flashid))

def _format_anchor(page):
    return '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page)

def _format_internal_page(match):
    story = match.group(1)
    page = match.group(3)
    if page == None:
        page = '{0:06}'.format(first_page(story))
    return '../{0}/{1}.html'.format(story, page)

def _format_internal_image(match):
    filename = match.group(1)
    return '../{0}"'.format(filename)

def _rewrite_links(text):
    text = re.sub(site_prefix+r'\?s=(\d*)(&amp;p=(\d*))?', _format_internal_page, text)
    text = re.sub(site_prefix+r'(.*)"', _format_internal_image, text)
    return text

def _rewrite_dialogue(text):
    return text
