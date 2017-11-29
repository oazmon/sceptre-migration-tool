# -*- coding: utf-8 -*-

import logging


__author__ = 'Intuit'
__email__ = 'oazmon@intuit.com'
__version__ = '0.0.1'


# Set up logging to ``/dev/null`` like a library is supposed to.
# http://docs.python.org/3.3/howto/logging.html#configuring-logging-for-a-library
class NullHandler(logging.Handler):  # pragma: no cover
    def emit(self, record):
        pass


logging.getLogger('sceptre_migration_tool').addHandler(NullHandler())
