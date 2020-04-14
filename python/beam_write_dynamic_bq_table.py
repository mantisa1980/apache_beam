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
from apache_beam.io import WriteToBigQuery
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import os
from apache_beam.pvalue import TaggedOutput
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/duyhsieh/gcp/keys/dragon-test-270305-90d9e89c44ca.json"

g_backend_tables = ['T3', 'T4']
g_project_id = 'dragon-test-270305'
g_dataset = 'backend_log'

class ParseBackendLog(beam.DoFn):
    def process(self, element):
        e = json.loads(element)
        yield TaggedOutput(e.pop('_Dest'), e)

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
        '--max-workers=1',
  ])
    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
    with beam.Pipeline(options=pipeline_options) as p:
        elements = (p | "CreatePCollectionData" >> beam.Create([
            json.dumps({'_Dest': 'T3', 'X': 'AAA', 'Y':123 }),
            json.dumps({'_Dest': 'T4', 'X': 'BBB', 'Y':456 }),
        ]))

        # output multi pcollections ; yield TaggedOutput('T3', element) goes to T3 pcollection
        processed_tagged_log = elements | "multiplex-pcoll" >> beam.ParDo(ParseBackendLog()).with_outputs(*g_backend_tables)  
        for key in g_backend_tables:
            processed_tagged_log[key] | "WriteBQ_%s" % key >> WriteToBigQuery(
               table=key,
               dataset=g_dataset,
               project=g_project_id,
               write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
                                   

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    run()
