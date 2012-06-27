#!/usr/bin/env python
from collections import deque
import argparse
import mspa
import archive

#parse args
cmdline = argparse.ArgumentParser(description='Download MS Paint Adventures stories in an archival format.', add_help=True)
arguments = cmdline.add_argument_group('arguments')
arguments.add_argument('story', default=6, nargs='?', type=int, help='Story to download - default 6 for Homestuck')
arguments.add_argument('page', type=int, help='Page on which to start download')

args = cmdline.parse_args()

#do archiving
archive.create_structure(args.story)

pages = ['{0:06}'.format(args.page)]
for page in pages:
    next_pages = mspa.get_page(args.story, page)
    pages.extend(next_pages)
