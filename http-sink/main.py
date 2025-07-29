# import the Quix Streams modules for interacting with Kafka.
# For general info, see https://quix.io/docs/quix-streams/introduction.html
# For sinks, see https://quix.io/docs/quix-streams/connectors/sinks/index.html
from quixstreams import Application
from quixstreams.sinks import BatchingSink, SinkBatch, SinkBackpressureError

import os
import time
import requests
import json

# for local dev, you can load env vars from a .env file
# from dotenv import load_dotenv
# load_dotenv()


class HttpSink(BatchingSink):
    """
    HTTP Sink that POSTs each message to a gateway endpoint.
    """
    def __init__(self):
        super().__init__()
        self.base_url = os.environ["RECEIVER_URL"]
        self.auth_token = os.environ["RECEIVER_AUTH_TOKEN"]
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.auth_token}"
            }
        )

    def _post_message(self, message_key, message_data):
        """POST message to the gateway endpoint"""
        url = f"{self.base_url}/{message_key}"
        response = self.session.post(url, json=message_data, timeout=30)
        response.raise_for_status()
        return response

    def write(self, batch: SinkBatch):
        """
        Write batch of messages to HTTP endpoint.
        Each message is POSTed individually to the gateway with its key.
        """
        attempts_remaining = 3
        
        while attempts_remaining:
            try:
                for item in batch:
                    message_key = item.key if item.key else "unknown"
                    message_data = item.value
                    self._post_message(message_key, message_data)
                return
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                attempts_remaining -= 1
                if attempts_remaining:
                    time.sleep(3)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    raise SinkBackpressureError(
                        retry_after=30.0,
                        topic=batch.topic,
                        partition=batch.partition,
                    )
                else:
                    raise
        raise Exception("Error while posting to HTTP endpoint")


def main():
    """ Here we will set up our Application. """

    # Setup necessary objects
    app = Application(
        consumer_group="http-sink",
        auto_create_topics=True,
        auto_offset_reset="earliest"
    )
    http_sink = HttpSink()
    input_topic = app.topic(name=os.environ["input"])
    sdf = app.dataframe(topic=input_topic)

    # Do SDF operations/transformations
    sdf = sdf.group_by("machine")

    # Finish by calling StreamingDataFrame.sink()
    sdf.sink(http_sink)

    # With our pipeline defined, now run the Application
    app.run()


# It is recommended to execute Applications under a conditional main
if __name__ == "__main__":
    main()