from assemblage.consts import RATELIMIT_URL
import json
import requests
import pprint
import time

pp = pprint.PrettyPrinter()

with open("assemblage/configure/scraper_config.json") as f:
    config = json.loads(f.read())


for token in config["git_token"]:
    r = requests.get(RATELIMIT_URL, auth=(token, token))
    rdict = json.loads(r.text)
    print(token)
    pp.pprint(rdict)
