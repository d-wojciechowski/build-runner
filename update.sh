#!/bin/bash

json=`curl -L -H "Accept: application/vnd.github+json" -H "X-GitHub-Api-Version: 2022-11-28" https://api.github.com/repos/d-wojciechowski/build-runner/releases/latest`
url=`echo "$json" | grep -oP '"browser_download_url": "\K[^"]+'`
wget -O wc_builder "$url"