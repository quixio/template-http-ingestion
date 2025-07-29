# Starter transformation

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/destinations/starter_destination) demonstrates how use the Quix Streams Sink framework to create
a custom HTTP sink, which will send data from a kafka topic to a desired HTTP endpoint.

Note that this is also set up to utilize an auth token, as set by the user.

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **input**: Name of the input topic to listen to.
- **RECEIVER_URL**: What HTTP receiver endpoint to send data to.
- **RECEIVER_AUTH_TOKEN**: The token for authenticating with an HTTP data receiver.

## Using Premade Sinks

This particular example uses a custom-made sink.

However, Quix Streams has numerous prebuilt sinks available to use out of the box, so be 
sure to [check them out!](https://quix.io/docs/quix-streams/connectors/sinks/index.html)


## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.