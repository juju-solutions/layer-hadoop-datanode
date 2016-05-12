from charms.reactive import when, when_not, set_state, remove_state
from charms.layer.apache_bigtop_base import Bigtop, get_layer_opts
from charmhelpers.core import host, hookenv


@when('bigtop.available', 'namenode.joined')
@when_not('apache-bigtop-datanode.installed')
def install_datanode(namenode):
    """Install if the namenode has sent its FQDN.

    We only need the namenode FQDN to perform the datanode install, so poll for
    namenodes() data whenever we have a namenode relation. This allows us to
    install asap, even if 'namenode.ready' is not set yet.
    """
    if namenode.namenodes():
        hookenv.status_set('maintenance', 'installing datanode')
        nn_host = namenode.namenodes()[0]
        bigtop = Bigtop()
        hosts = {'namenode': nn_host}
        bigtop.render_site_yaml(hosts=hosts, roles='datanode')
        bigtop.trigger_puppet()
        set_state('apache-bigtop-datanode.installed')
        hookenv.status_set('maintenance', 'datanode installed')


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
    bigtop.setup_hdfs()

    set_state('apache-bigtop-datanode.started')
    hookenv.status_set('maintenance', 'datanode started')


@when('apache-bigtop-datanode.started')
@when_not('namenode.ready')
def stop_datanode():
    hookenv.status_set('maintenance', 'stopping datanode')
    for port in get_layer_opts().exposed_ports('datanode'):
        hookenv.close_port(port)
    host.service_stop('hadoop-hdfs-datanode')
    remove_state('apache-bigtop-datanode.started')
    # NB: Remove the installed state so we can re-configure the installation
    # if/when a new namenode comes along in the future.
    remove_state('apache-bigtop-datanode.installed')
    hookenv.status_set('maintenance', 'datanode stopped')
