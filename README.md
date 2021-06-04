# wallstreetbets <a href="https://brrr.money/"><img src="./img/moneyprinter.gif" width="25" height="25" /></a>  
only💎👐allowed🚀🌙  
https://kennybui-datamleng.github.io/wallstreetbets/

    .
    ├── wsb                           # main scripts
    |   ├── moneyprinter.py           # print tendies
    |   ├── models.py                 # data models kinda
    |   ├── base.py                   # super classes
    |   └── credentials.json          # Reddit app client. Ask admin for access to the app client.
    ├── tests                         # Unit and integration tests 
    ├── tools
    |   ├── refresh_token.py          # manual tool to generate refresh token
    |   └── rewrite_pretty_json.py    # rewrite json with proper indent. use if json prints in single line.
    ├── LICENSE
    └── README.md

# usage
```
python moneyprinter.py -h 

usage: moneyprinter.py [-h] [-c CREDENTIALS]
                       [-t {all,day,hour,month,week,year}] [-l LIMIT]
                       [-o OUTPUT] [-st] [-d] [-dd]

Money Printer Go BRRRRRRR

optional arguments:
  -h, --help            show this help message and exit
  -c CREDENTIALS, --credentials CREDENTIALS
                        Credentials file. Default is ./credentials.json
  -t {all,day,hour,month,week,year}, --timefilter {all,day,hour,month,week,year}
                        Choose time filter for Reddit search query. Only used
                        for top and search methods. Default is day
  -l LIMIT, --limit LIMIT
                        Number of posts returned from Reddit search query. If
                        limit is None, then fetch as many entries as possible.
                        Most of reddit’s listings contain a maximum of 1000
                        items, and are returned 100 at a time. Default is None
  -o OUTPUT, --output OUTPUT
                        output folder for model. Default is ../output
  -st, --stockticker    Stock Ticker search. Default is False
  -d, --dailydiscussion
                        Daily Discussion flair. Default is False
  -dd, --duediligence   Due Diligence flair. Default is False
```

# setup
`pip install virtualenvwrapper` _(optional)_  
Windows is virtualenvwrapper-win
- if using Linux, refer to `venvsetup.sh`
- command shortlist ([docs](https://virtualenvwrapper.readthedocs.io/en/latest/command_ref.html)):
```
# create a venv
mkvirtualenv <venv name>

# use the venv
workon <venv name>

# add a path to the venv's Python path. useful for testing
add2virtualenv <path>
```

Inside your venv, `pip install -r requirements.txt`

Register for [Reddit API](https://github.com/reddit-archive/reddit/wiki/OAuth2) and create OAuth2 creds.  
**_NOTE:_** There is an existing Reddit app available, but feel free to create your own and replace the info in credentials.json

Use [PRAW](https://github.com/praw-dev/praw) to extract from Reddit ([docs](https://praw.readthedocs.io/en/latest/index.html))

# stock ticker list
nyse-listed.csv downloaded from [here](https://datahub.io/core/nyse-other-listings#data)  
nasdaq-list.csv downloaded from [here](https://datahub.io/core/nasdaq-listings)

# ~~python-highchart problems~~
~~python-highchart has javascript reference problems. requirements.txt has a fixed version.~~  
We are using [Altair](https://altair-viz.github.io/index.html) now! 😄

---
to the moon babyyyyyyy 🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🌙
