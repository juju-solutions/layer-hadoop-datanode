from charms.reactive import when, when_not, set_state, remove_state
from charms.layer.apache_bigtop_base import get_bigtop_base
from charmhelpers.core import host, hookenv

datanode_port = '50075'
@when_not('datanode.started')
def start_datanode():
    bigtop = get_bigtop_base()
    host.service_start('hadoop-hdfs-datanode')
    hookenv.open_port(datanode_port) # TODO need to read the ports from layer.yaml
    set_state('datanode.started')


@when('datanode.started')
@when_not('namenode.ready')
def stop_datanode():
    bigtop = get_bigtop_base()
    host.service_stop('hadoop-hdfs-datanode')
    hookenv.close_port(datanode_port)  # TODO need to read the ports from layer.yaml
    remove_state('datanode.started')
