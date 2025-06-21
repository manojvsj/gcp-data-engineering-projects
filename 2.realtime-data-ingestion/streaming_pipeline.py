import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

class ParseMessage(beam.DoFn):
    def process(self, element):
        record = json.loads(element.decode("utf-8"))
        yield {
            "user_id": record.get("user_id"),
            "action": record.get("action"),
            "timestamp": record.get("timestamp")
        }

def run():
    options = PipelineOptions()
    options.view_as(StandardOptions).streaming = True
    options.view_as(StandardOptions).runner = "DirectRunner"  # use DataflowRunner on GCP

    project_id = ""
    dataset_id = ""
    table = ""
    subscription_id = ""

    input_subscription = f"projects/{project_id}/subscriptions/{subscription_id}"
    output_table = f"{project_id}:{dataset_id}.{table}"

    schema = "user_id:INTEGER,action:STRING,timestamp:FLOAT"

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(subscription=input_subscription)
            | "Parse JSON" >> beam.ParDo(ParseMessage())
            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                output_table,
                schema=schema,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
            )
        )

if __name__ == "__main__":
    run()
