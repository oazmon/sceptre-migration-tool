# -*- coding: utf-8 -*-
import abc
import six
import logging


@six.add_metaclass(abc.ABCMeta)
class ReverseResolver():
    """
    ReverseResolver is an abstract base class that should be inherited by all
    reverse-resolvers. Environment config and the connection manager are
    supplied to the class, as they may be of use to inheriting classes.

    :param environment_config: The environment_config from config.yaml files.
    :type environment_config: sceptre.config.Config
    :param connection_manager: A connection manager.
    :type connection_manager: sceptre.connection_manager.ConnectionManager
    :param argument: Arguments to pass to the resolver.
    :type argument: str
    """

    def __init__(
        self,
        connection_manager=None,
        environment_config=None
    ):
        self.logger = logging.getLogger(__name__)
        self.environment_config = environment_config
        self.connection_manager = connection_manager

    @abc.abstractmethod
    def precendence(self):
        """
        An integer between 1 and 99 (inclusive) which indicates precedence
        of the reverse resolver. Lower values indicate higher precedence.
        """
        pass

    @abc.abstractmethod
    def suggest(self, argument):
        """
        An abstract method which must be overwritten by all inheriting classes.
        This method is called to reverse resolve a value into a call to a
        resolver in the config's parameters.
        Implementation of this method in subclasses must return a suitable
        string, or None to indicate they are unable to resolve.
        """
        pass  # pragma: no cover
