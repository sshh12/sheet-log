import urllib.request
import base64
import json
import io


class SheetLogError(Exception):
    pass


def _construct_payload(item):
    payload = []
    for key, val in item.items():
        if isinstance(val, str):
            payload.append({"key": key, "type": "string", "value": val})
        elif isinstance(val, float) or isinstance(key, int):
            payload.append({"key": key, "type": "number", "value": val})
        elif isinstance(val, dict) and "type" in val:
            payload.append({"key": key, **val})
        else:
            payload.append({"key": key, "type": "string", "value": repr(val)})
    return payload


class SheetLog:
    def __init__(self, app_url, spreadsheet_id, assert_check=True):
        if not app_url.startswith("https://"):
            app_url = "https://script.google.com/macros/s/{}/exec".format(app_url)
        self.app_url = app_url
        self.spreadsheet_id = spreadsheet_id
        if assert_check:
            assert self.check(), "Fail to connect to app script."

    def check(self):
        resp = self._post({"spreadsheet_id": self.spreadsheet_id, "payload": {}, "mode": "check"})
        return resp["status"] == "ok"

    def add(self, item, sheet="sheetlog"):
        payload = _construct_payload(item)
        return self._post({"spreadsheet_id": self.spreadsheet_id, "payload": payload, "mode": "append", "sheet": sheet})

    def _add_tab(self, tab_name, item):
        tab_name = str(tab_name)
        payload = _construct_payload(item)
        return self._post(
            {"spreadsheet_id": self.spreadsheet_id, "payload": payload, "tab_name": tab_name, "mode": "append-tab"}
        )

    def _update(self, search_key, search_value, item):
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
        resp = urllib.request.urlopen(req, body_enc).read()
        try:
            resp_body = json.loads(resp.decode("ascii"))
        except (UnicodeDecodeError, json.decoder.JSONDecodeError):
            raise SheetLogError("Could not decode response " + repr(resp))
        return resp_body