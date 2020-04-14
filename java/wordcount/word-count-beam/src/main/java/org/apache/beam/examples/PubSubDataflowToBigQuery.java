/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.apache.beam.examples;

import org.apache.beam.examples.common.ExampleUtils;
import org.apache.beam.examples.common.*;
import org.apache.beam.sdk.io.TextIO;
import org.apache.beam.sdk.transforms.windowing.FixedWindows;
import org.apache.beam.sdk.transforms.windowing.Window;
import org.apache.beam.sdk.transforms.ParDo;
import org.apache.beam.sdk.transforms.DoFn;
import org.joda.time.Duration;
import java.io.IOException;
import org.apache.beam.sdk.options.Default;
import org.apache.beam.sdk.options.Description;
import org.apache.beam.sdk.options.PipelineOptions;
import org.apache.beam.sdk.options.PipelineOptionsFactory;
import org.apache.beam.sdk.options.StreamingOptions;
import org.apache.beam.sdk.options.Validation.Required;


import org.apache.beam.sdk.io.gcp.pubsub.PubsubIO;
import org.apache.beam.sdk.io.gcp.pubsub.PubsubOptions;
import org.apache.beam.sdk.Pipeline;
//import static org.apache.beam.vendor.guava.v26_0_jre.com.google.common.base.MoreObjects.firstNonNull;
//import javax.annotation.Nullable;
//import org.apache.beam.sdk.io.FileBasedSink;
//import org.apache.beam.sdk.io.FileBasedSink.FilenamePolicy;
//import org.apache.beam.sdk.io.FileBasedSink.OutputFileHints;
//import org.apache.beam.sdk.io.TextIO;
//import org.apache.beam.sdk.io.fs.ResolveOptions.StandardResolveOptions;
//import org.apache.beam.sdk.io.fs.ResourceId;
//import org.apache.beam.sdk.transforms.DoFn;
//import org.apache.beam.sdk.transforms.PTransform;
//import org.apache.beam.sdk.transforms.windowing.BoundedWindow;
//import org.apache.beam.sdk.transforms.windowing.IntervalWindow;
//import org.apache.beam.sdk.transforms.windowing.PaneInfo;
//import org.apache.beam.sdk.values.PCollection;
//import org.apache.beam.sdk.values.PDone;
//import org.joda.time.format.DateTimeFormatter;
//import org.joda.time.format.ISODateTimeFormat;





public class PubSubDataflowToBigQuery {
    public interface PubSubToConsole extends StreamingOptions {
      @Description("Pub/Sub subscription to read from.")
      String getInputSubscription();
      void setInputSubscription(String value);

      //@Description("BigQuery table to write to, in the form 'project:dataset.table' or 'dataset.table'.")
      //@Default.String("beam_samples.streaming_beam_sql")
      //String getOutputTable();
      //void setOutputTable(String value);
    }
	  public static void main(String[] args) throws IOException {
	    // The maximum number of shards when writing output.
	    int numShards = 1;

	    //StreamingOptions options = PipelineOptionsFactory
	    //  .fromArgs(args)
	    //  .withValidation()
	    //  .as(StreamingOptions.class);
	    //options.setStreaming(true);

      PipelineOptions options = PipelineOptionsFactory
        .fromArgs(args)
        .as(PubSubToConsole.class);

	    Pipeline pipeline = Pipeline.create(options);
        // 1) Read string messages from a Pub/Sub topic.
        // 2) Group the messages into fixed-sized minute intervals.
        // 3) Write one file to GCS for every window of messages.
	    
      
      pipeline.
      apply(
        "Read PubSub Messages", PubsubIO.readStrings().fromSubscription("projects/dragon-test-270305/subscriptions/mytopic_listener"))
      .apply("PrintToStdout", ParDo.of(new DoFn<String, Void>() {
        @ProcessElement
          public void processElement(ProcessContext c) {
            System.out.printf("Received at %s\n", c.element()); // debug log
          }
      }));

      //  .apply("Write PubSub Events", PubsubIO.writeMessages().to(options.getOutputTopic()));
	    //  .apply(TextIO.write().to(options.getOutput()));
	    pipeline.run().waitUntilFinish();
	  }
	}

/*

class WriteOneFilePerWindow extends PTransform<PCollection<String>, PDone> {
  private static final DateTimeFormatter FORMATTER = ISODateTimeFormat.hourMinute();
  private String filenamePrefix;
  @Nullable private Integer numShards;

  public WriteOneFilePerWindow(String filenamePrefix, Integer numShards) {
    this.filenamePrefix = filenamePrefix;
    this.numShards = numShards;
  }

  @Override
  public PDone expand(PCollection<String> input) {
    ResourceId resource = FileBasedSink.convertToFileResourceIfPossible(filenamePrefix);
    TextIO.Write write =
        TextIO.write()
            .to(new PerWindowFiles(resource))
            .withTempDirectory(resource.getCurrentDirectory())
            .withWindowedWrites();
    if (numShards != null) {
      write = write.withNumShards(numShards);
    }
    return input.apply(write);
  }

  public static class PerWindowFiles extends FilenamePolicy {

    private final ResourceId baseFilename;

    public PerWindowFiles(ResourceId baseFilename) {
      this.baseFilename = baseFilename;
    }

    public String filenamePrefixForWindow(IntervalWindow window) {
      String prefix =
          baseFilename.isDirectory() ? "" : firstNonNull(baseFilename.getFilename(), "");
      return String.format(
          "%s-%s-%s", prefix, FORMATTER.print(window.start()), FORMATTER.print(window.end()));
    }

    @Override
    public ResourceId windowedFilename(
        int shardNumber,
        int numShards,
        BoundedWindow window,
        PaneInfo paneInfo,
        OutputFileHints outputFileHints) {
      IntervalWindow intervalWindow = (IntervalWindow) window;
      String filename =
          String.format(
              "%s-%s-of-%s%s",
              filenamePrefixForWindow(intervalWindow),
              shardNumber,
              numShards,
              outputFileHints.getSuggestedFilenameSuffix());
      return baseFilename
          .getCurrentDirectory()
          .resolve(filename, StandardResolveOptions.RESOLVE_FILE);
    }

    @Override
    public ResourceId unwindowedFilename(
        int shardNumber, int numShards, OutputFileHints outputFileHints) {
      throw new UnsupportedOperationException("Unsupported.");
    }
  }
}

public class PubSubDataflowToBigQuery {
    public interface PubSubToGCSOptions extends PipelineOptions, StreamingOptions {
      @Description("The Cloud Pub/Sub topic to read from.")
      @Required
      String getInputTopic();
      void setInputTopic(String value);

      @Description("Output file's window size in number of minutes.")
      @Default.Integer(1)
      Integer getWindowSize();
      void setWindowSize(Integer value);

      @Description("Path of the output file including its filename prefix.")
      @Required
      String getOutput();
      void setOutput(String value);
    }

    public static void main(String[] args) throws IOException {
      // The maximum number of shards when writing output.
      int numShards = 1;

      PubSubToGCSOptions options = PipelineOptionsFactory
        .fromArgs(args)
        .withValidation()
        .as(PubSubToGCSOptions.class);

      options.setStreaming(true);

      Pipeline pipeline = Pipeline.create(options);

      pipeline
        // 1) Read string messages from a Pub/Sub topic.
        .apply("Read PubSub Messages", PubsubIO.readStrings().fromSubscription("projects/dragon-test-270305/subscriptions/mytopic_listener"))
        // 2) Group the messages into fixed-sized minute intervals.
        //.apply(Window.into(FixedWindows.of(Duration.standardMinutes(options.getWindowSize()))))
        // 3) Write one file to GCS for every window of messages.
        //.apply("WriteToLocal",new WriteOneFilePerWindow("/tmp", numShards));

      // Execute the pipeline and wait until it finishes running.
      pipeline.run().waitUntilFinish();
    }
  }
*/
