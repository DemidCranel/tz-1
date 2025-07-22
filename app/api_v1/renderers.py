import csv
from io import StringIO

from rest_framework.renderers import BaseRenderer


class CSVRenderer(BaseRenderer):
    media_type = "text/csv"
    format = "csv"
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        if data is None:
            return ""
        if isinstance(data, list):
            data = {"results": data}
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data["results"][0].keys())
        writer.writeheader()
        for item in data["results"]:
            writer.writerow(item)
        return output.getvalue()
