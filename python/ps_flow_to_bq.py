#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
import logging
import re
import json
import traceback

from past.builtins import unicode
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/duyhsieh/gcp/keys/dragon-test-270305-90d9e89c44ca.json"


class ParseBackendLog(beam.DoFn):
    def __init__(self):
        pass

    def process(self, text):
        try:
            data = json.loads(text)
            return (data,)
        except:
            #data = {
            #    'BQTargetTable':'BQErrorLog',
            #    'SourceMessage':text,
            #    'ErrorMessage':str(traceback.format_exc()),
            #}
            #return (data,)
            return tuple()

def run(argv=None, save_main_session=True):
    pipeline_args = []
    pipeline_args.extend([
      # CHANGE 2/5: (OPTIONAL) Change this to DataflowRunner to
      # run your pipeline on the Google Cloud Dataflow Service.
      '--runner=DirectRunner',
      #'--runner=dataflow',
      # CHANGE 3/5: Your project ID is required in order to run your pipeline on
      # the Google Cloud Dataflow Service.
      '--project=dragon-test-270305',
      # CHANGE 4/5: Your Google Cloud Storage path is required for staging local
      # files.
      '--staging_location=gs://duysdf/',
      # CHANGE 5/5: Your Google Cloud Storage path is required for temporary
      # files.
      '--temp_location=gs://duysdf/temp',
      '--job_name=backend_log_dataflow_to_bigquery',
      '--streaming',
      '--region=asia-southeast1',
      '--max-workers=3',
  ])
  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    with beam.Pipeline(options=pipeline_options) as p:
    # 指定topic則會動態產生一個subscription
      # p | beam.io.ReadFromPubSub(topic='projects/dragon-test-270305/topics/mytopic', subscription='projects/dragon-test-270305/subscriptions/mytopic_listener')
        p | "ReadBackendLogFromPubSub" >> beam.io.ReadFromPubSub(subscription='projects/dragon-test-270305/subscriptions/mytopic_listener')
        p | "ParseBackendLogString" >> beam.ParDo(ParseBackendLog())
        p | 'WriteToBigQuery' >> beam.io.WriteToBigQuery(
            table='DFTest', dataset='backend_log', project='dragon-test-270305',
            create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
        #p | "WriteToText" >> WriteToText('/tmp/result')

if __name__ == '__main__':
  #logging.getLogger().setLevel(logging.DEBUG)
  logging.getLogger().setLevel(logging.INFO)
  run()
