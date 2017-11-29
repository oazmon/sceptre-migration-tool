# -*- coding: utf-8 -*-

from sceptre.exceptions import SceptreException


class ImportFailureError(SceptreException):
    """
    Error raised when import of a stack from AWS fails.
    """
