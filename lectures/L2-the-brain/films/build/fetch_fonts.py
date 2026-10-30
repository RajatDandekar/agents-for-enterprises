"""Run inside the composite image build: Google Sans Flex + Google Sans Code TTFs from Google Fonts into /fonts."""
import os
import re
import urllib.request

CSS = ("https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@300;400;500;600;700"
       "&family=Google+Sans+Code:wght@400;500;600&display=swap")
os.makedirs("/fonts", exist_ok=True)
css = urllib.request.urlopen(urllib.request.Request(CSS, headers={"User-Agent": "curl/8"})).read().decode()
for fam, wt, url in re.findall(r"font-family: '([^']+)';.*?font-weight: (\d+);.*?url\(([^)]+)\)", css, re.S):
    name = f"/fonts/{fam.replace(' ', '')}-{wt}.ttf"
    if not os.path.exists(name):
        open(name, "wb").write(urllib.request.urlopen(url).read())
        print(name, os.path.getsize(name))
