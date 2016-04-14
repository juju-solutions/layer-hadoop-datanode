from charms.reactive import when, when_not, set_state, remove_state
from charms.layer.apache_bigtop_base import get_bigtop_base
from charms.layer.apache_bigtop_datanode import get_layer_opts
from charmhelpers.core import host, hookenv


@when_not('namenode.joined')
def blocked():
    hookenv.status_set('blocked', 'waiting for namenode relation')


@when('namenode.joined')
@when_not('datanode.installed')
def install_hadoop(namenode):
    '''Install only if the namenode has sent its FQDN.'''
    if namenode.namenodes():
        hookenv.status_set('maintenance', 'installing datanode')
        hostname = namenode.namenodes()[0]
        bigtop = get_bigtop_base()
        bigtop.install(NN=hostname)
        set_state('datanode.installed')
        hookenv.status_set('maintenance', 'datanode installed')
    else:
        hookenv.status_set('waiting', 'waiting for namenode to become ready')


@when('datanode.installed')
@when_not('datanode.started')
def start_datanode():
    hookenv.status_set('maintenance', 'starting datanode')
    host.service_start('hadoop-hdfs-datanode')
    for port in get_layer_opts().exposed_ports('datanode'):
        hookenv.open_port(port)
    set_state('datanode.started')
    hookenv.status_set('active', 'ready')


@when('datanode.started')
@when_not('namenode.joined')
def stop_datanode():
    hookenv.status_set('maintenance', 'stopping datanode')
    for port in get_layer_opts().exposed_ports('datanode'):
        hookenv.close_port(port)
    host.service_stop('hadoop-hdfs-datanode')
    remove_state('datanode.started')
    hookenv.status_set('maintenance', 'datanode stopped')
