from jujubigdata.utils import DistConfig
from charms import layer


def get_layer_opts():
    return DistConfig(data=layer.options('apache-bigtop-base'))
