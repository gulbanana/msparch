from itertools import repeat

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
        return ['storyfiles/hs2', 'storyfiles/hs2/scraps', 'storyfiles/hs2/scratch', 'storyfiles/hs2/songs/alterniaboundsongs', 'cascade', 'scraps', 'scraps2', 'extras']
    elif story == 'ryanquest':
        return ['ryanquest']
    else:
        raise Exception('story id {0} unknown'.format(story))

def encoding(story):
    if story == 'ryanquest' or int(story) < 5:
        return 'iso-8859-1'
    else:
        return 'utf-8'

_alt_texts = []
_alt_texts.extend(repeat('', 92))
_alt_texts.extend([
    "BOOYEAH", 
    "... the FUCK?",
    "Oh hell no. He's talking about ancestors, isn't he.",
    "He's keeping little girls locked up in weird rooms, and rambling about troll ancestors. I just know it.",
    "NOT IN MY FUCKING COMIC.",
    "Oh, damn. This place is bigger than I thought. Any idea which way he went? Come on guys, help me out.",
    "I bet he's behind this door. YOU HEAR ME SCRATCH, THE JIG IS UP.", 
    "Ah-ha! Caught red handed, you bastard. You stop clogging up my story with your troll fanfiction this instaAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAH",
    "That was not the right door.",
    "This looks like the right place. The hallway is all round and shit. Just like his big stupid head.",
    "MY BEAUTIFUL PANELS WHAT HAS HE DONE. That son of a bitch. It's going to take so many sweeps to clean this mess up. So very, very many sweeps.",
    "God dammit, he's got a bowl full of these things?? He's pulling his snooty horseshit candy bowl stunts to mock my little arrows now. Excellent host my ass.",
    "RAAARARRAAUUUAAAAUUAGHGHGGHGGGGHHGH! *flip*",
    "Oh my god how can these possibly be so delicious???",
    "Whoa, better go easy on these. Might need some later.",
    "There you are. Go ahead, keep talking cueball. I've got you in the crosshairs of my broombristles. I have GOT you you pompous motherfucker.",
    "Tick. Tock. Tick. Tock. Tick. Tock. My heartbeat falls in rhythm with the clock as I draw close to my prey. I leave nothing to chance, for you see it is the most dangerous prey of all, a four foot tall asshole in suspenders who won't shut up. Wait for it, Hussie. Wait for it...",
    "RAAARARRAAUUUAAAAUUAGHGHGGHGGGGHHGH! *trip*",
    "bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap bap",
    "Everybody is fed up with your condescending, self indulgent narrative style. They want to go back to my slightly less condescending, slightly more self indulgent style."
])

def _room(number):
    room = 'room{0:02}.gif'.format(number)

    if number < 112:
        alt_text = _alt_texts[number]
        alt_img = None
    else:
        alt_text = ''
        alt_img = number - 112

    return (room, alt_text, alt_img)

def scratch_banner(page):
    try:
        page = int(page)
    except ValueError:
        return (None, None, None)

    if page < 5664 or page > 5981:
        return (None, None, None)

    # initial static room
    elif page < 5697:
        return ('room.gif', '', None)

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
