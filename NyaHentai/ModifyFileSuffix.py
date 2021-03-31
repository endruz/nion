#!/usr/bin/env python3
# coding=utf-8

import os

path = ""

oldSuffix = ".png"
newSuffix = ".jpg"


def modifySuffix(path, oldSuffix, newSuffix):
    path = path.strip()
    if os.path.exists(path) and os.path.isfile(path) and path.endswith(oldSuffix):
        newPath = path[:-len(oldSuffix)] + newSuffix
        os.rename(path, newPath)


if __name__ == "__main__":
    if os.path.isdir(path):
        for filename in os.listdir(path):
            subPath = os.path.join(path, filename)
            if os.path.isfile(subPath):
                modifySuffix(subPath, oldSuffix, newSuffix)
    elif os.path.isfile(path):
        modifySuffix(path, oldSuffix, newSuffix)
