from Tools import *
from Login import *
import json
import faulthandler

faulthandler.enable()
# Keep this code so everytime the program runs, it will validate the cookie
session = Login()
session.load_cookie()
session.check_login()

pTagList = {}
resp = get_history_list(session.session)
if resp is not None:
    for i in resp:
        if isinstance(i, str):
            bvid = i
        else:
            if i < 0.2 or i > 0.6:
                try:
                    tags = get_tag_from_bvid(bvid)
                    for i2 in tags:

                        try:
                            pTagList[i2] += 1
                        except KeyError:
                            pTagList[i2] = 1
                except:
                    pass

print(pTagList)

