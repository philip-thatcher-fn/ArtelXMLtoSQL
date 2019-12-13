# Python code to illustrate parsing of XML files
def loadRSS(url):
    resp = requests.get(url)
    with open('topnewsfeed.xml', 'wb') as f:
        f.write(resp.content)

loadRSS('http://www.hindustantimes.com/rss/topnews/rssfeed.xml')