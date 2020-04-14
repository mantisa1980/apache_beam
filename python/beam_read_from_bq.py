#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
import logging
import re

from past.builtins import unicode
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/duyhsieh/igs/bigquery/credentials/dragon-backend-test-10469db40798.json"

def run(argv=None, save_main_session=True):
  parser = argparse.ArgumentParser()
  parser.add_argument('--input',
                      dest='input',
                      default='gs://dataflow-samples/shakespeare/kinglear.txt',
                      help='Input file to process.')
  parser.add_argument('--output',
                      dest='output',
                      # CHANGE 1/5: The Google Cloud Storage path is required
                      # for outputting the results.
                      #default='gs://duy-dataflow/output',
                      default='/tmp/abcd',
                      help='Output file to write results to.')
  _, pipeline_args = parser.parse_known_args(argv)

  pipeline_args.extend([
      # CHANGE 2/5: (OPTIONAL) Change this to DataflowRunner to
      # run your pipeline on the Google Cloud Dataflow Service.
      '--runner=DirectRunner',
      #'--runner=DataflowRunner',
      # CHANGE 3/5: Your project ID is required in order to run your pipeline on
      # the Google Cloud Dataflow Service.
      '--project=dragon-backend-test',
      # CHANGE 4/5: Your Google Cloud Storage path is required for staging local
      # files.
      '--staging_location=gs://duy_dataflow/staging',
      # CHANGE 5/5: Your Google Cloud Storage path is required for temporary
      # files.
      '--temp_location=gs://duy_dataflow/temp',
      '--job_name=etljob',
  ])

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  pipeline_options = PipelineOptions(pipeline_args)
  pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
  with beam.Pipeline(options=pipeline_options) as p:

    query_results = p | beam.io.Read(
      beam.io.BigQuerySource(
        query='SELECT UserID, ClickEventID FROM dbo.ClickLog LIMIT 10',
        use_standard_sql=True,
        )
    )

    # Write the output using a "Write" transform that has side effects.
    # pylint: disable=expression-not-assigned
    query_results | WriteToText('gs://duy_dataflow/output/result')


if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
