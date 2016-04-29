## Overview

The Apache Hadoop software library is a framework that allows for the
distributed processing of large data sets across clusters of computers
using a simple programming model.

This charm deploys the DataNode component of the Apache Bigtop platform
to provide HDFS storage resources.


## Usage

This charm is intended to be deployed via one of the
[apache bigtop bundles](https://jujucharms.com/u/bigdata-dev/#bundles).
For example:

    juju quickstart bigtop-processing-mapreduce

This will deploy the Apache Bigtop platform with a workload node
preconfigured to work with the cluster.

You can also manually load and run map-reduce jobs via the plugin charm
included in the bundles linked above:

    juju scp my-job.jar plugin/0:
    juju ssh plugin/0
    hadoop jar my-job.jar


## Status and Smoke Test

Apache Bigtop charms provide extended status reporting to indicate when they
are ready:

    juju status --format=tabular

This is particularly useful when combined with `watch` to track the on-going
progress of the deployment:

    watch -n 0.5 juju status --format=tabular

The message for each unit will provide information about that unit's state.
Once they all indicate that they are ready, you can perform a "smoke test"
to verify HDFS or YARN services are working as expected. Trigger the
`smoke-test` action by:

    juju action do namenode/0 smoke-test
    juju action do resourcemanager/0 smoke-test

After a few seconds or so, you can check the results of the smoke test:

    juju action status

You will see `status: completed` if the smoke test was successful, or
`status: failed` if it was not.  You can get more information on why it failed
via:

    juju action fetch <action-id>


## Scaling

To scale your cluster storage capabilities, you can simply add more datanode
units.  For example, to add three more units:

    juju add-unit datanode -n 3


## Deploying in Network-Restricted Environments

Charms can be deployed in environments with limited network access. To deploy
in this environment, you will need a local mirror to serve required packages.


### Mirroring Packages

You can setup a local mirror for apt packages using squid-deb-proxy.
For instructions on configuring juju to use this, see the
[Juju Proxy Documentation](https://juju.ubuntu.com/docs/howto-proxies.html).


## Contact Information

- <bigdata@lists.ubuntu.com>


## Hadoop

- [Apache Bigtop](http://bigtop.apache.org/) home page
- [Apache Bigtop issue tracking](http://bigtop.apache.org/issue-tracking.html)
- [Apache Bigtop mailing lists](http://bigtop.apache.org/mail-lists.html)
- [Apache Bigtop charms](https://jujucharms.com/q/apache/bigtop)
