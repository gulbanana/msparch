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

def dirs(story):
    if story == '1':
        return ['advimgs/jb', 'advimgs/jb/lv2_option1', 'advimgs/jb/lv2_option2', 'advimgs/jb/lv3', 'advimgs/jb/lv4', 'storyfiles/jb2']
    elif story == '2':
        return ['advimgs/bq']
    elif story == '4':
        return ['advimgs/ps', 'extras']
    elif story == '5':
        return ['storyfiles/hs']
    elif story == '6':
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps', 'scraps2']
    elif story == 'ryanquest':
        return ['ryanquest']
    else:
        raise Exception('story id {0} unknown'.format(story))
