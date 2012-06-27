import os

def create_structure(story):
    os.makedirs(story_dir(story+'/scraps'), exist_ok=True)
    os.makedirs('{0}'.format(story), exist_ok=True)

def story_dir(story):
    if story == 6:
        return "storyfiles/hs2"
    else:
        raise Exception('story number ' + story + ' unknown')

def save_page(story, page, data):
    f = open('{0}/{1:06}.txt'.format(story, page), 'wb')
    f.write(data)
    f.close()

def save_image(story, image, data):
    f = open('{0}/{1}'.format(story_dir(story), image), 'wb')
    f.write(data)
    f.close()
