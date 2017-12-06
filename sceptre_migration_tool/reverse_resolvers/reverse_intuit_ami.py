'''
Created on Nov 29, 2017

@author: Omer Azmon
'''
import re

from sceptre_migration_tool.reverse_resolvers import ReverseResolver


class ReverseIntuitAmi(ReverseResolver):

    def __init__(self, *args, **kwargs):
        super(ReverseIntuitAmi, self).__init__(*args, **kwargs)

    def precendence(self):
        return 90

    def suggest(self, value):
        return '!intuit_ami' if re.match('ami-[0-9af]+$', value) else None
