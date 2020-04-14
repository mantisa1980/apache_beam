#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import argparse
import logging
import re
import json
import traceback
import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/duyhsieh/gcp/keys/dragon-test-270305-90d9e89c44ca.json"


def my_print(element):
    print "my_print:", element

# X -> Map ->x (still 1 pcollection element)
# (X,X,X) -> Map ->(x, x, x) (still 1 Pcollection element)
# (X,X,X) -> FlatMap ->x, x, x (3 Pcollection elements) , so input must be iteratable, other exception will occur (i.e., unboxing)

# A Map transform, maps from a PCollection of N elements into another PCollection of N elements.
def test_map():
    # The result is a collection of THREE lists: [[1, 'any'], [2, 'any'], [3, 'any']]
    with beam.Pipeline() as p: # 最後會做p.run, p.wait_until_finish()
        p | beam.Create([1, 2, 3]) | beam.Map(lambda x: [x, 'any']) | beam.Map(my_print)  # 會把p變成pcollection, 但p應該是要維持pipeline型態

# A FlatMap transform maps a PCollections of N elements into N collections of zero or more elements, which are then flattened into a single PCollection.
def test_flatmap():
    # The lists that are output by the lambda, are then flattened into a
    # collection of SIX single elements: [1, 'any', 2, 'any', 3, 'any']
    with beam.Pipeline() as p: # 最後會做p.run, p.wait_until_finish()
        p | beam.Create([1, 2, 3]) | beam.FlatMap(lambda x: [x, 'any']) | beam.Map(my_print)  # 會把p變成pcollection, 但p應該是要維持pipeline型態
        
def test_map2():
    with beam.Pipeline() as p:
        p | beam.Create([1, 2, 3]) | beam.Map(lambda x: x ) | beam.Map(my_print)

def test_flatmap2(): # error
    with beam.Pipeline() as p: 
        p | beam.Create([1, 2, 3]) | beam.FlatMap(lambda x: x ) | beam.Map(my_print) 

def console_print1():
    data = ["this is sample data", "this is yet another sample data"]
    pipeline = beam.Pipeline()
    counts = (pipeline | "create" >> beam.Create(data)
        | "split" >> beam.ParDo(lambda row: row.split(" "))
        | "pair" >> beam.Map(lambda w: (w, 1))
        | "group" >> beam.CombinePerKey(sum))  # group ('this', 1) and ('this', 1) becomes ('this', 2)

    # lets collect our result with a map transformation into output array
    output = []
    def collect(row):
        output.append(row)
        return True

    counts | "print" >> beam.Map(collect)

    result = pipeline.run()
    result.wait_until_finish()
    print output

# 要思考成流水線一樣, 不是一個一個當下改變狀態 (ex. declarative language)
def console_print2():
    # lets have a sample string
    data = ["this is sample data", "this is yet another sample data"]

    # create a pipeline
    pipeline = beam.Pipeline()
    counts = (pipeline | "create" >> beam.Create(data)
        | "split" >> beam.ParDo(lambda row: row.split(" "))
        | "pair" >> beam.Map(lambda w: (w, 1))
        | "group" >> beam.CombinePerKey(sum) 
        | "print" >> beam.FlatMap(my_print)
        )

    result = pipeline.run()
    result.wait_until_finish()

#console_print1()
#test_map()
#test_flatmap2()
console_print2()