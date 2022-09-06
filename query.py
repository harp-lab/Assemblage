import requests
import json
import re


q = "pushed:2018-03-13T14:17:57..2018-03-13T21:17:57 language:c++ 'Project' in:sln"
payload = {'q': q, 'per_page': 100, 'page': 0}


PROXIES = ["",
            "http://i-04155ecba1cfdb2e9.us-west-1.compute.internal:3128"
            ]

for i in range(3):
    r = requests.get(
            "https://api.github.com/search/repositories",
            payload,
            proxies={
                    'https': PROXIES[i],
                }
            )

    rdict = json.loads(r.text)
    print(r.text[:100])
