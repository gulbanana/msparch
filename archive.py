import os

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

def save_image(story, image, data):
    f = open('{0}/{1}'.format(story_dir(story), image), 'wb')
    f.write(data)
    f.close()
