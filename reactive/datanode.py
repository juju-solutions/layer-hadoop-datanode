from charms.reactive import when, when_not, set_state, remove_state, is_state
from charms.reactive.helpers import data_changed
from charms.layer.apache_bigtop_base import (
    Bigtop, get_hadoop_version, get_layer_opts
)
from charmhelpers.core import host, hookenv
from jujubigdata import utils


@when('bigtop.available', 'namenode.joined')
def install_datanode(namenode):
    """
    Install if the namenode has sent its FQDN.

    We only need the namenode FQDN to perform the datanode install, so poll for
    namenodes() data whenever we have a namenode relation. This allows us to
    install asap, even if 'namenode.ready' is not set yet.
    """
    namenodes = namenode.namenodes()
    if namenodes and data_changed('datanode.namenodes', namenodes):
        installed = is_state('apache-bigtop-datanode.installed')
        action = 'installing' if not installed else 'configuring'
        hookenv.status_set('maintenance', '%s datanode' % action)
        bigtop = Bigtop()
        bigtop.render_site_yaml(
            hosts={
                'namenode': namenodes[0],
            },
            roles=[
                'datanode',
            ],
        )
        bigtop.queue_puppet()
        set_state('apache-bigtop-datanode.pending')


@when('apache-bigtop-datanode.pending')
@when_not('apache-bigtop-base.puppet_queued')
def finish_install_datanode():
    remove_state('apache-bigtop-datanode.pending')
    set_state('apache-bigtop-datanode.installed')
    installed = is_state('apache-bigtop-datanode.installed')
    action = 'installed' if not installed else 'configured'
    hookenv.status_set('maintenance', 'datanode %s' % action)


@when('apache-bigtop-datanode.installed', 'namenode.joined')
@when_not('namenode.ready')
def send_nn_spec(namenode):
    """Send our datanode spec so the namenode can become ready."""
    bigtop = Bigtop()
    namenode.set_local_spec(bigtop.spec())


@when('apache-bigtop-datanode.installed', 'namenode.ready')
@when_not('apache-bigtop-datanode.started')
def start_datanode(namenode):
    hookenv.status_set('maintenance', 'starting datanode')
    # NB: service should be started by install, but this may be handy in case
    # we have something that removes the .started state in the future. Also
    # note we restart here in case we modify conf between install and now.
    host.service_restart('hadoop-hdfs-datanode')
    for port in get_layer_opts().exposed_ports('datanode'):
        hookenv.open_port(port)

    # Create a /user/ubuntu dir in HDFS (this is safe to run multiple times).
    bigtop = Bigtop()
    if not bigtop.check_hdfs_setup():
        try:
            utils.wait_for_hdfs(30)
            bigtop.setup_hdfs()
        except utils.TimeoutError:
            # HDFS is not yet available or is still in safe mode, so we can't
            # do the initial setup (create dirs); skip setting the state below
            # so that, on the next hook, we try again.
            hookenv.status_set('waiting', 'waiting on hdfs')
            return

    set_state('apache-bigtop-datanode.started')
    hookenv.application_version_set(get_hadoop_version())
    hookenv.status_set('maintenance', 'datanode started')


@when('apache-bigtop-datanode.started')
@when_not('namenode.ready')
def stop_datanode():
    hookenv.status_set('maintenance', 'stopping datanode')
    for port in get_layer_opts().exposed_ports('datanode'):
        hookenv.close_port(port)
    host.service_stop('hadoop-hdfs-datanode')
    remove_state('apache-bigtop-datanode.started')
    hookenv.status_set('maintenance', 'datanode stopped')
