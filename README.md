# Simple HTTP Ingestion Project Template

This example project demonstrates how to receive data from an HTTP endpoint, 
do some normalizations, and then publish the augmented data to an InfluxDB2 database.

It also includes visualization/dashboard examples using Grafana (which queries InfluxDB2).



## Project Architecture

-DIAGRAMS HERE-



## Configuration

There are various things that can be tweaked, like the name of the InfluxDB database. 
However, everything in this template has predefined values except secrets, which will
require defining upon deployment of this project.

### Required Secrets

These will be requested once this project template is deployed:

- **influxdb_admin_token**
- **influxdb_admin_password**
- **http_auth_token**



## Data Operations Overview

### Event Structure
```json
{
  "srv_ts": 1753717885782747100,
  "connector_ts": 1753717885792584200,
  "type": "Double",
  "val": 198.54935414815827,
  "param": "T002",
  "machine": "3D_PRINTER_2"
}
```

The HTTP source will receive IoT events from a sensor (`machine`) that contain a value (`val`) for a given measurement 
(`param`), along with the timestamp it was generated at (`srv_ts`).

In total, there are 2 different parameters: `T001` and `T002`.

In this example, there is only 1 machine (`3D_PRINTER_2`).


### Normalizing Events

We will normalize these events so that rather than each parameter is no longer an individual
event.

Instead, we will aggregate all parameters so that for a given machine, we have the average
of each parameter over one second (determined by the event timestamp, `srv_ts`).

This will result in a new outgoing aggregate event:

```json
{
  "T001": 97.20716911943455,
  "machine": "3D_PRINTER_2",
  "T002": 194.41638423332338,
  "timestamp": "2025-07-28 15:52:51.600000"
}
```

This aggregation is done using a Quix Streams `tumbling_window` operation, found in the
`HTTP Data Normalization` application.


### InfluxDB2 Data

These events are then pushed to InfluxDB2 to database `my_bucket` under measurement 
`printers` (with `machine` as a tag).

-TABLE HERE-

## Grafana

-GRAFANA GRAPHS HERE-