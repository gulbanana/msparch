#!/usr/bin/env python
from collections import deque
from asq.initiators import query
import argparse
import mspa
import archive
import stories

#parse args
cmdline = argparse.ArgumentParser(description='Download MS Paint Adventures stories in an archival format.', add_help=True)
arguments = cmdline.add_argument_group('arguments')
arguments.add_argument('story', default='6', nargs='?', type=str, help='Story to download - defaults to 6 for Homestuck')
arguments.add_argument('page', type=int, default=0, nargs='?', help='Page on which to start download - defaults to start of story')

args = cmdline.parse_args()
if args.page == 0:
    args.page = stories.first_page(args.story)

archiver = archive.MirroringArchiver(args.story)
downloader = mspa.SiteReader(args.story, archiver)

pages = ['{0:06}'.format(args.page)]
for page in pages:
    next_pages = downloader.get_page(page)
    pages.extend(query(next_pages).difference(pages))

archiver.finalise()
