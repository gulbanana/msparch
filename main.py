#!/usr/bin/env python
from collections import deque
import os
import argparse
import mspa
import archive
import stories

#parse args
cmdline = argparse.ArgumentParser(description='Download MS Paint Adventures stories in an archival format.', add_help=True)
arguments = cmdline.add_argument_group('positional arguments')
arguments.add_argument('story', default='6', nargs='?', type=str, choices=['1','2','4','5','6','ryanquest'],
                       help='Story to download. Default 6 for Homestuck')
cmdline.add_argument('-p','--page', type=int, default=0, nargs='?', 
                     help='Page on which to start download. Default story start')
cmdline.add_argument('-d','--directory', type=str, default='MSPA', nargs='?', \
                     help='Location for downloaded files. Default MSPA/')

args = cmdline.parse_args()

if args.page == 0:
    args.page = stories.first_page(args.story)

archive.init(args.story, args.directory)
downloader = mspa.SiteReader(args.story)

pages = [('{0:06}'.format(args.page), None)]
for (page, source) in pages:
    next_pages = downloader.get_page(page, source)
    pages.extend([(p, s) for (p, s) in next_pages if p not in set(list(zip(*pages))[0])])

archive.finalise()
