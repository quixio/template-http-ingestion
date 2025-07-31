# import the Quix Streams modules for interacting with Kafka.
# For general info, see https://quix.io/docs/quix-streams/introduction.html
from quixstreams import Application
from quixstreams.dataframe.joins.lookups.postgresql import PostgresLookup

import os
from datetime import datetime

# for local dev, load env vars from a .env file
# from dotenv import load_dotenv
# load_dotenv()


def get_postgres_lookup() -> PostgresLookup:
    return PostgresLookup(
        host=os.environ["POSTGRES_HOST"],
        port=int(os.environ["POSTGRES_PORT"]),
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=os.environ["POSTGRES_DBNAME"],
    )


def config_apply(row: dict) -> dict:
    """
    Unpacks the printer machine configs retrieved from Postgres.
    The configs are a list of dicts that each look like:
    {"field_id": "T001", "field_name": "sensor_1", "field_scalar": .50}
    """
    for field_cfg in row.pop("configs"):
        new_value = row.pop(field_cfg["field_id"]) * field_cfg["field_scalar"]
        row[field_cfg["field_name"]] = new_value
    return row


def main():
    # App setup
    app = Application(
        consumer_group="http_data_normalization2",
        auto_create_topics=True,
        auto_offset_reset="earliest"
    )
    input_topic = app.topic(name=os.environ["input"])
    output_topic = app.topic(name=os.environ["output"])

    # Postgres setup
    postgres_lookup = get_postgres_lookup()
    postgres_lookup_fields = {
        "configs": postgres_lookup.field(
            table="printer_configs",
            columns=["field_id", "field_name", "field_scalar"],
            on="printer_id",
            first_match_only=False,
            ttl=30.0,
        )
    }

    # SDF operations to pull the configs from Postgres and then apply them
    sdf = app.dataframe(topic=input_topic)
    sdf = sdf.join_lookup(
        lookup=postgres_lookup,
        fields=postgres_lookup_fields,
        on="machine",
    ).apply(config_apply)

    # Finish off by writing to the final result to the output topic
    sdf.to_topic(output_topic, key=lambda row: row["machine"])

    # With our pipeline defined, now run the Application
    app.run()


# It is recommended to execute Applications under a conditional main
if __name__ == "__main__":
    main()
