#!/usr/bin/env python3
# coding=utf-8

import os
import re
import time
import requests
from pprint import pprint
from datetime import datetime


urls = []

for url in urls:

    content = requests.get(url).text

    title = re.findall(r'<title>.*?</title>', content)[0].lstrip("<title>").rstrip("</title>").strip()

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {title} start...')

    path = f'./download/{title}'
    if not os.path.exists(path):
        os.makedirs(name=path, exist_ok=True)

    src_list = {src[5:-1] for src in re.findall(r'src="https://[0-9a-z.]*?/galleries/\d*?/.*?\.(?:png|jpg)"', content)}

    saved_list = set()
    if os.path.exists(f'{path}/savedfile'):
        with open(f'{path}/savedfile', 'r') as f:
            saved_list = {line.strip() for line in f.readlines()}

    src_list = list(src_list - saved_list)

    src_list.sort()
    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] picture src list:')
    pprint(src_list)

    for src in src_list:
        file_name = src.split('/')[-1]
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] downloading {path}/{file_name} ...')
        for i in range(5):
            try:
                response = requests.get(src, timeout=60)
            except requests.exceptions.Timeout:
                print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] connect {src} timeout !')
            else:
                img = response.content
                with open(f'{path}/{file_name}', 'wb') as f:
                    f.write(img)
                time.sleep(3)
        if os.path.exists(f'{path}/{file_name}'):
            with open(f'{path}/savedfile', 'a') as f:
                f.write(f'{src}\n')
        else:
            with open(f'{path}/missingfile', 'a') as f:
                f.write(f'{src}\n')

    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {title} over!')
