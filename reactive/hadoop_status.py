# pylint: disable=unused-argument
from charms.reactive import is_state, when, when_not
from charmhelpers.core.hookenv import status_set


@when_not('apache-bigtop-datanode.started')
def prereq_status():
    hdfs_rel = is_state('namenode.joined')
    hdfs_ready = is_state('namenode.ready')

    if not hdfs_rel:
        status_set('blocked', 'missing required namenode relation')
    elif hdfs_rel and not hdfs_ready:
        status_set('waiting', 'waiting for hdfs to become ready')


@when('apache-bigtop-datanode.started')
def ready_status():
    status_set('active', 'ready')
