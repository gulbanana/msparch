import os
import sys
import re

template_file = open('template.html', 'r')
template = template_file.read()
template_file.close()

def create_structure(story):
    os.makedirs(story_dir(story)+'/scraps', exist_ok=True)
    os.makedirs('{0}'.format(story), exist_ok=True)

def story_dir(story):
    if story == 1:
        return "advimgs/jb"
    if story == 2:
        return "advimgs/bq"
    elif story == 6:
        return "storyfiles/hs2"
    else:
        raise Exception('story number ' + story + ' unknown')

def save_page(story, page, data):
    f = open('{0}/{1}.txt'.format(story, page), 'wb')
    f.write(data)
    f.close()

def page_exists(story, page):
    return os.path.exists('{0}/{1}.txt'.format(story, page))

def page_command(story, page):
    f = open('{0}/{1}.txt'.format(story, page), 'r')
    text = f.readline().strip()
    f.close()
    return text

def save_image(story, image, data):
    f = open('{0}/{1}'.format(story_dir(story), image), 'wb')
    f.write(data)
    f.close()

def gen_html(story, page, command, assets, content, links):
    print('>',command)
    sys.stdout.flush()

    images = map(lambda url: '<img src="../{0}"/>'.format(url[33:]), assets)

    anchors = map(lambda page: '<font size="5">&gt; <a href="{0}.html">{0}</a></font><br>'.format(page), links)

    html = template.format(command=command, assets='<br><br>'.join(images), narration='<br>'.join(content), navigation=''.join(anchors))
    
    f = open('{0}/{1}.html'.format(story, page), 'w')
    f.write(html)
    f.close()

def fix_links(story):
    pages = filter(lambda path: path.endswith('.html'), os.listdir(str(story)))
    for page in pages:
        f = open('{0}/{1}'.format(story, page), 'r')
        text = f.read()
        f.close()

        text = re.sub(r'>(\d*)</a>', lambda match: '>{0}</a>'.format(page_command(story, match.group(1))), text)

        f = open('{0}/{1}'.format(story, page), 'w')
        f.write(text)
        f.close()
