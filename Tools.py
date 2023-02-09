import json
import requests


def find_info_from_dict(source: str, valueFinding):
    result = []
    repeat = False
    for i in range(len(source)):
        if source[i:i + len(valueFinding)] == valueFinding and source[i + len(valueFinding) + 4: i + len(valueFinding) + 3 + source[i + len(valueFinding) + 4:].find(",")] != " ":
            result.append(source[i + len(valueFinding) + 4: i + len(valueFinding) + 3 + source[i + len(valueFinding) + 4:].find(",")])
        if valueFinding == "bvid":
            if source[i:i + 8] == "progress":
                watched = int(source[i + 10: i + 10 + source[(i + 10):].find(",")])
            elif source[i:i + 8] == "duration":
                    result.append(watched / int(source[i + 10: i + 10 + source[(i + 10):].find(",")]))

    return result


def get_recommend_video(session):
    header = {
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0"
    }

    session.headers = header
    resp = session.get("https://www.bilibili.com/").text
    resp = resp.split("recommended-container")[1].split("<script>window.__INITIAL_DATA__")[0]

    bvids = get_substrings(resp, "https://www.bilibili.com/video/", 12)
    for i in bvids:
        bvids.remove(i)

    return bvids


def get_history_list(session):
    newVideo = []
    skipProgress = False
    url = "https://api.bilibili.com/x/web-interface/history/cursor"
    historyList = session.get(url).json()
    try:
        with open("historyList.json", "r") as f:
            existingVideos = json.load(f)
    except:
        existingVideos = {}
    bvidPair = find_info_from_dict(str(historyList), "bvid")
    if bvidPair is not None:
        for i in bvidPair:

            if isinstance(i, str):
                try:
                    temp = existingVideos[i]
                    skipProgress = True
                except KeyError:
                    existingVideos[i] = None
                    newVideo.append(i)
            elif isinstance(i, float):
                if not skipProgress:
                    existingVideos[list(existingVideos.keys())[-1]] = i
                    newVideo.append(i)
                else:
                    skipProgress = False
    with open("historyList.json", "w") as f:
        json.dump(existingVideos, f)

    return newVideo

def get_tag_from_bvid(bvid):
    url = "https://api.bilibili.com/x/web-interface/view/detail"
    params = {"bvid": bvid}
    resp = requests.get(url, params=params).json()
    if resp["code"] == 0:
        tags = find_info_from_dict(str(resp), "tag_name")
        return tags
    else:
        return None


def get_substrings(string, target, length):
    substrings = []
    start = 0
    while True:
        start = string.find(target, start) + len(target)
        if start == len(target) - 1:
            break
        end = start + length
        substrings.append(string[start:end])
    return substrings


"""#Password login method
token, gt, challenge = getCaptcha()
validate, seccode = captchaCertify(gt, challenge)
encodedPassword = encryptPassword()
resp = login(encodedPassword, token, challenge, validate, seccode)
print(resp.json())
"""

# Get the current history list
"""resp = qr_generate()
login_by_qr(resp, loginSession)
history_list(loginSession)"""
