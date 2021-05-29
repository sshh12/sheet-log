import urllib.request
import json
import base64
import io


def _construct_payload(item):
    payload = []
    for key, val in item.items():
        if isinstance(val, str):
            payload.append({"key": key, "type": "string", "value": val})
        elif isinstance(val, float) or isinstance(key, int):
            payload.append({"key": key, "type": "number", "value": val})
        elif isinstance(val, dict) and "type" in val:
            payload.append({"key": key, **val})
    return payload


class SheetLog:
    def __init__(self, app_url, spreadsheet_id):
        self.app_url = app_url
        self.spreadsheet_id = spreadsheet_id

    def add(self, item):
        payload = _construct_payload(item)
        self._post({"spreadsheet_id": self.spreadsheet_id, "payload": payload, "mode": "append"})

    def update(self, search_key, search_value, item):
        payload = _construct_payload(item)
        self._post(
            {
                "spreadsheet_id": self.spreadsheet_id,
                "payload": payload,
                "mode": "update",
                "search_key": search_key,
                "search_value": search_value,
            }
        )

    def get_current_plot(self, name="image"):
        import matplotlib.pyplot as plt

        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        encoded_buf = base64.b64encode(buf.read()).decode("ascii")
        return {"type": "image_b64", "value": encoded_buf, "name": name, "content_type": "image/png"}

    def _post(self, body):
        body_enc = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(self.app_url)
        req.add_header("Content-Type", "application/json; charset=utf-8")
        req.add_header("Content-Length", len(body_enc))
        resp = urllib.request.urlopen(req, body_enc)
        print(resp.read())