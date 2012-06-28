#!/usr/bin/env python
from collections import deque
from asq.initiators import query
import argparse
import mspa
import archive

#parse args
cmdline = argparse.ArgumentParser(description='Download MS Paint Adventures stories in an archival format.', add_help=True)
arguments = cmdline.add_argument_group('arguments')
arguments.add_argument('story', default=6, nargs='?', type=int, help='Story to download - default 6 for Homestuck')
arguments.add_argument('page', type=int, default=0, nargs='?', help='Page on which to start download')

args = cmdline.parse_args()
if args.page == 0:
    args.page = mspa.first_page(args.story)

#do archiving
archive.create_structure(args.story)

pages = ['{0:06}'.format(args.page)]
for page in pages:
    next_pages = mspa.get_page(args.story, page)
    pages.extend(query(next_pages).difference(pages))

archive.fix_links(args.story)
