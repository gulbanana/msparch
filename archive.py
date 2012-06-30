import os
import sys
import re

with open('template.html', 'r') as template_file:
    _template = template_file.read()
_site_prefix = 'http://www.mspaintadventures.com/'

### stories ###
def initialise(story):
    os.makedirs('{0}'.format(story), exist_ok=True)
    for directory in _story_dirs(story):
        os.makedirs(directory, exist_ok=True)

def finalise(story):
    pages = filter(lambda path: path.endswith('.html'), os.listdir(str(story)))
    for page in pages:
        with open('{0}/{1}'.format(story, page), 'r') as pagefile:
            text = pagefile.read()

        text = re.sub(r'>((jb2_)?\d*)</a>', lambda match: '>{0}</a>'.format(_page_command(story, match.group(1))), text)

        with open('{0}/{1}'.format(story, page), 'w') as pagefile:
            pagefile.write(text)

def first_page(story):
    story = int(story)
    if story == 1:
        return 2
    elif story == 2:
        return 136
    elif story == 4:
        return 219
    else:
        raise Exception('story id {0} not supported'.format(story))

def _story_dirs(story):
    story = int(story)
    if story == 1:
        return ['advimgs/jb', 'advimgs/jb/lv2_option1', 'advimgs/jb/lv2_option2', 'advimgs/jb/lv3', 'advimgs/jb/lv4', 'storyfiles/jb2']
    elif story == 2:
        return ['advimgs/bq']
    elif story == 4:
        return ['advimgs/ps', 'extras']
    elif story == 5:
        return ['storyfiles/hs']
    elif story == 6:
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps']
    else:
        raise Exception('story number {0} unknown'.format(story))

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

### html output ###
def gen_html(story, page, command, assets, content, links):
    print('>',command)
    sys.stdout.flush()

    images = map(_format_image, assets)

    anchors = map(lambda page: '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page), links)

    content = map(_rewrite_links, content)
    content = _rewrite_dialogue(content)

    html = _template.format(command=command, assets='<br><br>'.join(images), narration='<br>'.join(content), navigation=''.join(anchors))
    
    with open('{0}/{1}.html'.format(story, page), 'w') as f:
        f.write(html)

def _format_image(url):
    return '<img src="../{0}"/>'.format(url[33:])

def _format_internal_link(match):
    story = match.group(1)
    page = match.group(3)
    if page == None:
        page = '{0:6}'.format(first_page(story))
    return '../{0}/{1}.html'.format(story, page)

def _rewrite_links(text):
    text = re.sub(_site_prefix+r'\?s=(\d*)(&amp;p=(\d*))?', _format_internal_link, text)
    return text

def _rewrite_dialogue(text):
    return text
