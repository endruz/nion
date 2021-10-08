#!/usr/bin/env python3
# coding=utf-8

import os
import re
import json
import httpx
import asyncio
import aiofiles

from PIL import Image
from typing import List, Tuple, Set
from multiprocessing import Pool

from datetime import datetime

"""
多进程 + 协程异步 I/O 爬虫
"""


class NyaHentaiSpyder:
    def __init__(self, urls: List[str], processes: int, save_path: str) -> None:
        self.urls = urls
        self.processes = processes
        self.save_path = save_path

    @staticmethod
    def is_damaged(path: str) -> bool:
        damaged = False
        try:
            Image.open(path).load()
        except OSError:
            damaged = True
        return damaged

    def parse_page(self, url: str) -> Tuple[str, Set[str]]:
        content = httpx.get(url).text
        title = re.findall(r'<title>.*?</title>', content)[0].lstrip("<title>").rstrip("</title>").strip()

        src_list = {src[5:-1] for src in re.findall(r'src="https://[0-9a-z.]*?/galleries/\d*?/.*?\.(?:png|jpg)"', content)}
        return title, src_list

    def download_comic(self, url: str) -> None:
        title, src_list = self.parse_page(url)
        path = os.path.join(self.save_path, title)
        os.makedirs(name=path, exist_ok=True)
        if os.path.exists(os.path.join(path, "savedfile")):
            with open(os.path.join(path, "savedfile"), "r") as f:
                saved_list = {line.strip() for line in f.readlines()}
            src_list = src_list - saved_list
        src_list = list(src_list)
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {title} start...')
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] picture src list:')
        print(json.dumps(src_list, indent=4, ensure_ascii=False))

        tasks = [self.download_pic(src, path) for src in src_list]

        if tasks:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            # RuntimeError: Event loop is closed
            # loop.close()

        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] {title} over!')

    async def download_pic(self, src: str, path: str, retry: int = 5) -> None:
        file_name = src.split('/')[-1]
        save_path = os.path.join(path, file_name)
        is_finish = False
        print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] downloading {save_path} ...')
        async with httpx.AsyncClient() as client:
            for _ in range(retry):
                try:
                    response = await client.get(src, timeout=60)
                except httpx.TimeoutException:
                    print(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] connect {src} timeout !')
                else:
                    img = response.content
                    async with aiofiles.open(save_path, 'wb') as f:
                        f.write(img)
                    is_finish = not self.is_damaged(save_path)
                    if is_finish:
                        break

            if os.path.exists(save_path) and is_finish:
                with open(os.path.join(path, "savedfile"), 'a') as f:
                    f.write(f'{src}\n')
            # else:
            #     with open(os.path.join(path, "missingfile"), 'a') as f:
            #         f.write(f'{src}\n')

    def run(self) -> None:
        with Pool(self.processes) as p:
            p.map(self.download_comic, self.urls)


if __name__ == '__main__':
    urls = []
    processes = 5
    save_path = "./download"
    spyder = NyaHentaiSpyder(urls, processes, save_path)
    spyder.run()
