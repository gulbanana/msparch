import os
import sys
import re

template_file = open('template.html', 'r')
template = template_file.read()
template_file.close()

def create_structure(story):
    os.makedirs('{0}'.format(story), exist_ok=True)
    for directory in story_dirs(story):
        os.makedirs(directory, exist_ok=True)

def story_dirs(story):
    if story == 1:
        return ['advimgs/jb', 'advimgs/jb/lv2_option1', 'advimgs/jb/lv2_option2', 'advimgs/jb/lv3', 'advimgs/jb/lv4', 'storyfiles/jb2']
    elif story == 2:
        return ["advimgs/bq"]
    elif story == 4:
        return ["advimgs/ps"]
    elif story == 5:
        return ["storyfiles/hs"]
    elif story == 6:
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps']
    else:
        raise Exception('story number ' + story + ' unknown')

def save_page(story, page, data):
    with open('{0}/{1}.txt'.format(story, page), 'wb') as f:
        f.write(data)

def page_exists(story, page):
    return os.path.exists('{0}/{1}.txt'.format(story, page))

def load_page(story, page):
    with open('{0}/{1}.txt'.format(story, page), 'rb') as f:
        return f.read()

def page_command(story, page):
    with open('{0}/{1}.txt'.format(story, page), 'r') as f:
        return f.readline().strip()

def save_image(story, image, data):
    with open('{0}/{1}'.format(story_dirs(story)[0], image), 'wb') as f:
        f.write(data)

def image_exists(story, image):
    return os.path.exists('{0}/{1}'.format(story_dirs(story)[0], image))

def gen_html(story, page, command, assets, content, links):
    print('>',command)
    sys.stdout.flush()

    images = map(lambda url: '<img src="../{0}"/>'.format(url[33:]), assets)

    anchors = map(lambda page: '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page), links)

    html = template.format(command=command, assets='<br><br>'.join(images), narration='<br>'.join(content), navigation=''.join(anchors))
    
    with open('{0}/{1}.html'.format(story, page), 'w') as f:
        f.write(html)

def fix_links(story):
    pages = filter(lambda path: path.endswith('.html'), os.listdir(str(story)))
    for page in pages:
        with open('{0}/{1}'.format(story, page), 'r') as pagefile:
            text = pagefile.read()

        text = re.sub(r'>((jb2_)?\d*)</a>', lambda match: '>{0}</a>'.format(page_command(story, match.group(1))), text)

        with open('{0}/{1}'.format(story, page), 'w') as pagefile:
            pagefile.write(text)
