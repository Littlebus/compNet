try:
    from urlparse import urljoin, urlparse
except ImportError:
    from urllib.parse import urljoin, urlparse

from flask import redirect, request, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='/index', **kwargs):
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)
    return redirect(url_for(default, **kwargs))


def addtodict3(thedict, key_a, key_b, key_c):
    if key_a in thedict:
        if key_b in thedict[key_a]:
            if key_c in thedict[key_a][key_b]:
                thedict[key_a][key_b][key_c] += 1
            else:
                thedict[key_a][key_b].update({key_c: 1})
        else:
            thedict[key_a].update({key_b: {key_c: 1}})
    else:
        thedict.update({key_a: {key_b: {key_c: 1}}})
