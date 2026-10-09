import httplib2
import re
from urllib.parse import urlencode

http = httplib2.Http()
response, content = http.request("http://localhost:8000/")
status = response.status            # 200
print('status', '=', repr(status))
html = content.decode()             # the page as text
print('html', '=', repr(html))

version = httplib2.__version__      # '0.32.0'
print('version', '=', repr(version))



http = httplib2.Http()
response, content = http.request("http://localhost:8000/")
page = content.decode()
# '<html><head><title>Something.</title></head><body>Something.</body></html>'

stripped = re.sub(r"<[^<]+?>", "", content.decode())   # 'Something.Something.'
print('stripped', '=', repr(stripped))

http = httplib2.Http()
ok = http.request("http://localhost:8000/")[0].status            # 200
print('ok', '=', repr(ok))
missing = http.request("http://localhost:8000/news/")[0].status  # 404
print('missing', '=', repr(missing))

http = httplib2.Http()
resp = http.request("http://localhost:8000/", "HEAD")[0]
content_type = resp["content-type"]       # 'text/html; charset=utf-8'
print('content_type', '=', repr(content_type))
length = resp["content-length"]           # '74'
print('length', '=', repr(length))
server = resp["server"]                   # 'BaseHTTP/0.6 Python/3.14.6'
print('server', '=', repr(server))

http = httplib2.Http()
query = urlencode({"name": "Peter"})
greeting = http.request(f"http://localhost:8000/greet?{query}")[1].decode()   # 'Hello Peter'
print('greeting', '=', repr(greeting))

http = httplib2.Http()
body = urlencode({"name": "Peter"})
resp, content = http.request(
    "http://localhost:8000/greet",
    method="POST",
    headers={"Content-Type": "application/x-www-form-urlencoded"},
    body=body,
)
posted = content.decode()                 # 'Hello Peter'
print('posted', '=', repr(posted))

http = httplib2.Http()
put_status = http.request("http://localhost:8000/greet", "PUT", body="x")[0].status         # 501
print('put_status', '=', repr(put_status))
delete_status = http.request("http://localhost:8000/greet", "DELETE")[0].status            # 501
print('delete_status', '=', repr(delete_status))

http = httplib2.Http()
default_agent = http.request("http://localhost:8000/agent")[1].decode()
# 'Python-httplib2/0.32.0 (gzip)'
custom = http.request("http://localhost:8000/agent", headers={"User-Agent": "Python script"})[1].decode()
# 'Python script'

anon = httplib2.Http()
denied = anon.request("http://localhost:8000/secure/")[0].status      # 401
print('denied', '=', repr(denied))

auth = httplib2.Http()
auth.add_credentials("user7", "7user")
resp, content = auth.request("http://localhost:8000/secure/")
allowed = (resp.status, content.decode())   # (200, 'This is a secure page.')
print('allowed', '=', repr(allowed))

cached = httplib2.Http(".cache")
first = cached.request("http://localhost:8000/")[0].fromcache    # False
print('first', '=', repr(first))
second = cached.request("http://localhost:8000/")[0].fromcache   # True
print('second', '=', repr(second))

safe = httplib2.Http(timeout=5)
try:
    safe.request("http://localhost:9/")
except (ConnectionError, TimeoutError, httplib2.HttpLib2Error) as e:
    error = type(e).__name__              # 'ConnectionRefusedError'

def check_links(urls):
    client = httplib2.Http(timeout=5)
    report = {}
    for url in urls:
        try:
            report[url] = client.request(url, "HEAD")[0].status
        except (ConnectionError, TimeoutError, httplib2.HttpLib2Error) as e:
            report[url] = type(e).__name__
    return report

links = check_links(["http://localhost:8000/", "http://localhost:8000/old-page", "http://localhost:9/"])
# {'http://localhost:8000/': 200, 'http://localhost:8000/old-page': 404, 'http://localhost:9/': 'ConnectionRefusedError'}
