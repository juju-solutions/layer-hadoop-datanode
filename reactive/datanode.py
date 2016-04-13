from charms.reactive import when, when_not, set_state, remove_state
from charms.layer.apache_bigtop_base import get_bigtop_base
from jujubigdata.handlers import HDFS
from jujubigdata import utils


@when('namenode.ready')
@when_not('datanode.started')
def start_datanode(namenode):
    bigtop = get_bigtop_base()
    utils.install_ssh_key('hdfs', namenode.ssh_key())
    utils.manage_etc_hosts()
    # TODO add direct invocation to the init.d script
    utils.run_as('root', 'service', 'hadoop-hdfs-datanode', 'start')

    bigtop.open_ports('datanode')
    set_state('datanode.started')


@when('datanode.started')
@when_not('namenode.ready')
def stop_datanode():
    bigtop = get_bigtop_base()
    utils.run_as('root', 'service', 'hadoop-hdfs-datanode', 'stop')
    bigtop.close_ports('datanode')
    remove_state('datanode.started')


def restart_datanode(namenode):
    bigtop = get_bigtop_base()
    utils.install_ssh_key('hdfs', namenode.ssh_key())
    utils.manage_etc_hosts()
    # TODO add direct invocation to the init.d script
    utils.run_as('root', 'service', 'hadoop-hdfs-datanode', 'restart')

    bigtop.open_ports('datanode')
    set_state('datanode.started')
