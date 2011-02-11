import httplib
import urlparse
import json

def get_auth(username, key, auth_url):
    u = urlparse.urlparse(auth_url)
    cls = u.scheme == 'https' and httplib.HTTPSConnection or httplib.HTTPConnection
    h = cls(u.netloc)
    headers={"X-Auth-User" : username,
             "X-Auth-Key" : key
             }
    h.request("GET", u.path, headers=headers)
    ret={}
    for k, v in h.getresponse().getheaders():
        if k.startswith("x-"):
            ret[k.replace("x-", "")] = v
    return ret

def cs_get(auth, rest):
    u = urlparse.urlparse(auth["server-management-url"])
    cls = u.scheme == 'https' and httplib.HTTPSConnection or httplib.HTTPConnection
    h = cls(u.netloc)
    headers={"X-Auth-Token" : auth['auth-token']}
    h.request("GET", u.path + rest, headers=headers)    
    resp = h.getresponse()
    return resp

def get_servers(auth):
    return json.loads(cs_get(auth, "/servers/detail").read())['servers']

def get_images(auth):
    return json.loads(cs_get(auth, "/images/detail").read())['images']


if __name__ == '__main__':
    pass
