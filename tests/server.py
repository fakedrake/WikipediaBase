"""
A dumb server to mimic wikipedia. Pass "record" to the arguments
to run the tests recording missing values. The purpose is to be able
to test independently of wikipedia.org.
"""

import sys
import json
import urllib
from flask import Flask


app = Flask(__name__)
DATAFILE = "pages.json"
DATA = json.load(DATAFILE)

@app.route("/w/index.php")
def get_article():
    """
    Get article from local data store. If not found forward request to
    the real wikipedia and rectord the result.
    """

    global DATA

    key = json.dumps(request.args)
    ret = DATA.get(key)

    if ret:
        return ret

    if 'record' in sys.argv:
        with open(DATAFILE, 'w') as fp:
            ret = urllib.urlopen("http://wikipedia.org/w/index.php?"
                                 + urlencode(request.args)).read()
            DATA[key] = ret
            json.save(fp, DATA)
            return ret

    return None


if __name__ == '__main__':
    app.run()
