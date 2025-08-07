# import the Quix Streams modules for interacting with Kafka.
# For general info, see https://quix.io/docs/quix-streams/introduction.html
from quixstreams import Application

import os
from datetime import datetime

# for local dev, load env vars from a .env file
# from dotenv import load_dotenv
# load_dotenv()


def window_initializer(row: dict) -> dict:
    return {"machine": row["machine"]}


def window_reducer(agg: dict, row: dict) -> dict:
    agg.setdefault(row["param"], []).append(row["val"])
    return agg


def window_finalizer(finalized_window: dict):
    agg_values = finalized_window["value"]
    machine = agg_values.pop("machine")
    return {
        **{k: round(sum(v) / len(v), 2) for k, v in agg_values.items()},
        "timestamp": str(datetime.fromtimestamp(finalized_window["start"] / 1000)),
        "machine": machine
    }


def main():
    # Setup necessary objects
    app = Application(
        consumer_group="http_data_normalization",
        auto_create_topics=True,
        auto_offset_reset="earliest"
    )
    input_topic = app.topic(name=os.environ["input"], key_deserializer="str")
    output_topic = app.topic(name=os.environ["output"])
    sdf = app.dataframe(topic=input_topic)

    sdf["srv_ts"] = sdf.apply(lambda row: row["srv_ts"] if row["srv_ts"] is not None else row["connector_ts"])
    sdf = sdf.set_timestamp(lambda row, *_: int(row["srv_ts"] / 1E6))

    # Do StreamingDataFrame operations/transformations here
    sdf = sdf.hopping_window(1000, 200, 500).reduce(reducer=window_reducer, initializer=window_initializer).final()
    sdf = sdf.apply(window_finalizer)

    # Finish off by writing to the final result to the output topic
    sdf.to_topic(output_topic, key=lambda row: row["machine"])

    # With our pipeline defined, now run the Application
    app.run()


# It is recommended to execute Applications under a conditional main
if __name__ == "__main__":
    main()