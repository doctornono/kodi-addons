from bs4 import BeautifulSoup
import urllib
from urllib import request

import re
from scraperNoosfere import scraperNoosfere


myscrap = scraperNoosfere()
print(str(myscrap.scrapLivre('2146579743')))
print(str(myscrap.scrapCollection('-10246496')))
