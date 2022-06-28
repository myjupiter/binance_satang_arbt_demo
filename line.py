import requests
import json

def replyLine(obj):
    text = ""
    form_fields = {
            "to": str(userLine),
            "message": [
                {
                    "type": "text",
                    "text": text
                    }
                ]
            }
    obj = { "url": url, "form_fields": form_fields, "AccessToken": accessToken }

    accessToken = ""
    line_object = json.loads(str(obj))
    headers = {
            'content-type': 'application/json; charset=UTF-8',
            'Authorization': 'Bearer %s' % accessToken
            }
    data = json.dumps(line_objct['form_fields'])
    url = "https://api.line.me/v2/bot/message/push"
    userLine = ""
    r = requests.post(url, headers=headers, data=data, allow_redirects=True)
