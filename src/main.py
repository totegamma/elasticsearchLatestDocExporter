import os
import sys
import json
import flask
import requests
import textwrap
from dateutil import parser
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth

ELASTIC_USERNAME = os.getenv('ELASTIC_USERNAME')
ELASTIC_PASSWORD = os.getenv('ELASTIC_PASSWORD')
ELASTIC_ENDPOINT = os.getenv('ELASTIC_ENDPOINT')
ENTRY_COUNT = int(os.getenv('ENTRY_COUNT'))

app = flask.Flask(__name__)


@app.route("/metrics")
def export_metrics():
    metrics = textwrap.dedent('''\
    # HELP elasticsearch_latestdoc_elapsed_seconds The elapsed seconds from latest docment inserted
    # TYPE elasticsearch_latestdoc_elapsed_seconds gauge
    ''')
    print(ENTRY_COUNT, flush=True)
    for i in range(ENTRY_COUNT):
        print(i, flush=True)
        try:
            print(os.getenv(f"QUERY{i}"), flush=True);
            query = {
                "_source": False,
                "size": 1,
                "sort": {"@timestamp": "desc"},
                "query": json.loads(os.getenv(f"QUERY{i}")),
                "fields": ["@timestamp"]
            }
            result = requests.post(ELASTIC_ENDPOINT,
                                     auth=HTTPBasicAuth(ELASTIC_USERNAME, ELASTIC_PASSWORD),
                                     headers={'Content-Type': 'application/json'},
                                     data=json.dumps(query)).json()
            print(result, file=sys.stderr, flush=True)
            name = os.getenv(f"NAME{i}")
            latest = parser.parse(result['hits']['hits'][0]['fields']['@timestamp'][0])
            elapsed = datetime.now(timezone.utc) - latest
            metrics += f'elasticsearch_latestdoc_elapsed_seconds{{name="{name}"}} {elapsed.seconds}'
        except Exception as e:
            print(e, flush=True)
    return metrics


@app.route("/health")
def health():
    pass


if __name__ == "__main__":
    app.run(host='0.0.0.0')
