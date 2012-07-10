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
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps', 'storyfiles/hs2/scratch', 'scraps2']
    elif story == 'ryanquest':
        return ['ryanquest']
    else:
        raise Exception('story id {0} unknown'.format(story))

def _room(number):
    return 'room{0:02}.gif'.format(number)

def scratch_banner(page):
    page = int(page)
    if page < 5664 or page > 5981:
        return None

    # initial static room
    elif page < 5697:
        return 'room.gif'

    # first linear sequence
    elif page >= 5697 and page <= 5774:
        return _room(page-5695)

    # click-the-panels
    elif page == 5795:
        return _room(81)
    elif page == 5836:
        return _room(82)
    elif page == 5874:
        return _room(83)
    elif page >= 5775 and page <= 5901:
        return _room(80)
    elif page == 5902:
        return _room(84)
    elif page >= 5902 and page <= 5935:
        return _room(85)

    # handmaid strife
    elif page == 5936:
        return _room(86)
    elif page >= 5937 and page <= 5951:
        return _room(87)

    # hussie & LE - alt text from 5956
    elif page >= 5952 and page <= 5981:
        return _room(page-5864)

    else:
        raise Exception('Impossible scratch room number')
