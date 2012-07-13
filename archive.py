from urllib.request import urlretrieve
from urllib.parse import urlparse
import subprocess
import platform
import os
import sys
import re
import stories

### constants ###
site_prefix = 'http://www.mspaintadventures.com/'

### module lifetime ###
def init(storyid, storyloc):
    global story, root, archdir, appdir, swix
    story = storyid
    root = stories.dirs(story)[0]
    archdir = storyloc
    appdir = os.path.dirname(sys.argv[0])

    if platform.system() == 'Windows':
        swix = os.path.join(appdir, 'swfmill.exe')
    else:
        swix = os.path.join(appdir, 'swfmill')
        

    global _object_template, _log_template, _html_template, _sbahj_template, _scratch_template, _cascade_template, _dota_template, _index_template
    _object_template = _load_template('flash.txt')
    _log_template = _load_template('pesterlog.txt')
    _html_template = _load_template('page.txt')
    _sbahj_template = _load_template('page_sbahj.txt')
    _scratch_template = _load_template('page_scratch.txt')
    _cascade_template = _load_template('page_cascade.txt')
    _dota_template = _load_template('page_dota.txt')
    _index_template = _load_template('index.txt')

    _mkdir('images')
    _get_global('images/logo.gif')
    _get_global('images/title.png')
    _get_global('images/v2_blankstrip.gif')
    _get_global('images/v2_blanksquare.gif')
    _get_global('images/v2_blanksquare2.gif')
    _get_global('images/v2_blanksquare3.gif')
    _get_global('images/header_cascade.gif')
    _get_global('jquery.min.js')
    _get_global('ddimgtooltip.css')
    _get_global('ddimgtooltip.js')

    _mkdir('{0}'.format(story))
    for directory in stories.dirs(story):
        _mkdir(directory)

### cleanup ###
def finalise():
    _name_commands()
    _delete_xml()
    _gen_index()

def _name_commands():
    pages = filter(lambda path: path.endswith('.html'), os.listdir(os.path.join(archdir, story)))
    for page in pages:
        with open('{0}/{1}/{2}'.format(archdir, story, page), 'r') as pagefile:
            text = pagefile.read()
            text = re.sub(r'>((jb2_)?\d+)</a>', lambda match: '>{0}</a>'.format(_page_command(match.group(1))), text)

        with open('{0}/{1}/{2}'.format(archdir, story, page), 'w') as pagefile:
            pagefile.write(text)

def _delete_xml():
    flashes = [os.path.join(archdir, root, path) for path in os.listdir(os.path.join(archdir, root)) if re.match(r'\d\d\d\d\d$', path)]
    if os.path.exists(os.path.join(archdir,'cascade')):
        flashes += [os.path.join(archdir,'cascade')]

    for flashdir in flashes:
        for xml in filter(lambda file: file.endswith('.xml'), os.listdir(flashdir)):
            os.remove(flashdir + '/' + xml)

### filesystem helpers ###
def _load_template(filename):
    with open(os.path.join(appdir, 'templates', filename), 'r') as template_file:
        return template_file.read()

def _load_binary(directory, filename):
    with open(os.path.join(archdir, directory, filename), 'rb') as f:
        return f.read()

def _save_binary(directory, filename, data):
    filename = os.path.join(*filename.split('/'))
    with open(os.path.join(archdir, directory, filename), 'wb') as f:
        f.write(data)

def _exists(directory, filename):
    return os.path.exists(os.path.join(archdir, directory, filename))

def _get_global(filename):
    path = os.path.join(archdir, filename)
    if not os.path.exists(path):
        urlretrieve(site_prefix+filename, path)

def _mkdir(directory):
    os.makedirs(os.path.join(archdir, directory), exist_ok=True)

### pages ###
def save_page(page, data):
    _save_binary(story, _page_filename(page), data)

def page_exists(page):
    return _exists(story, _page_filename(page))

def page_load(page):
    return _load_binary(story, _page_filename(page))

def _page_command(page):
    with open(os.path.join(archdir, story, _page_filename(page)), 'rb') as f:
        return f.readline().decode(stories.encoding(story)).strip()

def _page_filename(page):
    return '{0}.txt'.format(page)

### images ###
def save_image(image, data):
    _save_binary(root, image, data)

def image_exists(image):
    return _exists(root, image)

### flash animations ###
def save_flash(flashid, script, data):
    flashdir = '{0}/{1}'.format(root, flashid)
    _mkdir(flashdir)
    _save_binary(flashdir, 'AC_RunActiveContent.js', script)
    _save_binary(flashdir, '{0}.swf'.format(flashid), data)
    _flash_fix_links(flashid)

def flash_exists(flashid):
    return _exists(root, flashid)

def flash_load(flashid):
    return _load_binary('{0}/{1}'.format(root, flashid), '{0}.swf'.format(flashid))

def flash_nexts(flashid):
    nexts = []
    xml = '{2}/{0}/{1}/{1}.xml'.format(root, flashid, archdir)
    swf = '{2}/{0}/{1}/{1}.swf'.format(root, flashid, archdir)
    
    if not os.path.exists(xml):
        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

    with open(xml, 'r', encoding='latin1') as f:    # note: swfmill generates files that CLAIM to be utf-8 but are not
        for line in f.readlines():
            match = re.search(r'(\d\d\d\d\d\d).html', line)
            if match:
                if int(match.group(1)) >= int(stories.first_page(story)):
                    nexts.append(match.group(1))
 
    return nexts

def _flash_fix_links(flashid):
    xml = '{2}/{0}/{1}/{1}.xml'.format(root, flashid, archdir)
    swf = '{2}/{0}/{1}/{1}.swf'.format(root, flashid, archdir)

    with open(os.devnull, 'w') as null:
        subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)
    
    # walkarounds don't need linkfixing and are broken by it
    if flashid in ['02791', '03318', '03077', '03435', '03692']:
        return

    with open(xml, 'r') as f:
        text = f.readlines()
    text = map(_rewrite_links, text)
    with open(xml, 'w') as f:
        f.writelines(text)

    with open(os.devnull, 'w') as null:
        subprocess.call([swix, 'xml2swf', xml, swf], stdout=null)

def _flash_dimensions(flashid):
    xml = '{2}/{0}/{1}/{1}.xml'.format(root, flashid, archdir)
    swf = '{2}/{0}/{1}/{1}.swf'.format(root, flashid, archdir)

    if not os.path.exists(xml):
        with open(os.devnull, 'w') as null:
            subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

    with open(xml, 'r', encoding='utf-8') as f:
        text = f.read(500)
        match = re.search(r'Rectangle left="0" right="(\d+)" top="0" bottom="(\d+)"', text)
        x = int(match.group(1)) / 20
        y = int(match.group(2)) / 20

    return [x, y]

### misc. assets and special cases ###
def save_misc(filename, data):
    if filename.endswith('/'):
        _mkdir(filename)
        _save_binary(filename, 'index.html', data)
    else:
        _save_binary('', filename, data)

def misc_exists(filename):
    if filename.endswith('/'):
        return _exists(filename, 'index.html')
    else:
        return _exists('', filename)

def misc_load(filename):
    if filename.endswith('/'):
        return _load_binary(filename, 'index.html')
    else:
        return _load_binary('', filename)

def logo_path(remote):
    components = len(remote.split('/'))
    return '../' * (components-1) + 'images/logo.gif'

### [S] Cascade segments ###
def save_cascade(prefix, filename, data):
    _save_binary('cascade', filename, data)

    cascade_prefix = prefix
    def _rewrite_cascade(line):
        return re.sub(cascade_prefix+r'(.*)"', lambda match: '../cascade/{0}"'.format(match.group(1)), line)

    swf = 'cascade/' + filename
    xml = swf.replace('swf', 'xml')

    with open(os.devnull, 'w') as null:
        subprocess.call([swix, 'swf2xml', swf, xml], stdout=null)

    with open(xml, 'r') as f:
        text = f.readlines()
    text = map(_rewrite_cascade, text)
    with open(xml, 'w') as f:
        f.writelines(text)

    with open(os.devnull, 'w') as null:
        subprocess.call([swix, 'xml2swf', xml, swf], stdout=null)

def cascade_exists(filename):
    return _exists('cascade', filename)


### HTML output ###
def _gen_index():
    first_page = '{0:06}'.format(stories.first_page(story))
    first_cmd = _page_command(first_page)
    print('[{0}]'.format(first_cmd))

    html = _index_template.format(
        command=first_cmd,
        story=story,
        page=first_page
    )

    with open(os.path.join(archdir, 'index.html'), 'w') as f:
        f.write(html)

def gen_html(page, command, assets, content, links):
    print('>', command.encode(sys.stdout.encoding, errors='ignore').decode(sys.stdout.encoding).replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&'))
    sys.stdout.flush()

    images = map(_format_asset, assets)
    anchors = map(_format_anchor, links)
    content = map(_rewrite_links, content)
    content = _rewrite_dialogue(list(content))

    room, alt, img = stories.scratch_banner(page)
    if room:
        banner = _format_banner(room)
        html = _scratch_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors), banner=banner, alt_text=alt, alt_img='imgtip[{0}]'.format(img))
    elif page == '005982':
        html = _sbahj_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
    elif page == '006009':
        html = _cascade_template.format(assets=_format_cascade(), navigation=''.join(anchors), banner='../images/header_cascade.gif')
    elif page == '006715':
        html = _dota_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
    else:
        html = _html_template.format(command=command, assets='<br/>\n<br/>\n'.join(images), narration='<br/>\n'.join(content), navigation=''.join(anchors))
    
    with open('{0}/{1}/{2}.html'.format(archdir, story, page), 'w') as f:
        f.write(html)

def _format_banner(roomfile):
    return '../{0}/scratch/{1}'.format(root, roomfile)

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

    w, h = _flash_dimensions(flashid)

    return _object_template.format(
        id='../{0}/{1}/{1}'.format(root, flashid), 
        swf='../{0}/{1}/{1}.swf'.format(root, flashid), 
        js='../{0}/{1}/AC_RunActiveContent.js'.format(root, flashid),
        width=str(w),
        height=str(h))

def _format_cascade():
    return _object_template.format(
        id='../cascade/cascade_loaderExt',
        swf='../cascade/cascade_loaderExt.swf',
        js='../cascade/AC_RunActiveContent.js',
        width='950',
        height='650')

def _format_anchor(page):
    return '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page)

def _format_internal_page(match):
    other_story = match.group(1)
    page = match.group(3)
    if page == None:
        page = '{0:06}'.format(stories.first_page(other_story))
    return '../{0}/{1}.html'.format(other_story, page)

def _format_internal_asset(match):
    filename = match.group(1)
    if 'sweetbroandhellajeff' in filename:
        return '{0}{1}"'.format(site_prefix, filename)
    else:
        return '../{0}"'.format(filename)

def _format_wv(match):
    vagabond = match.group(0)
    return '{0}index.html'.format(vagabond)

def _rewrite_links(text):
    text = re.sub(site_prefix+r'scratch\.php\?s=(\d*)(&amp;p=(\d*))?', _format_internal_page, text)
    text = re.sub(site_prefix+r'\?s=(\d*)(&amp;p=(\d*))?', _format_internal_page, text)
    text = re.sub(site_prefix+r'(.*)"', _format_internal_asset, text)
    text = re.sub(r'waywardvagabond/(.*?)/', _format_wv, text)
    return text

def _rewrite_dialogue(text):
    logtype = re.match(r'\|(.*)\|', text[0])

    if logtype != None:
        return [_log_template.format(title=logtype.group(1).capitalize(), pesterlog='<br/>\n'.join(text[1:]))]
            
    return text
