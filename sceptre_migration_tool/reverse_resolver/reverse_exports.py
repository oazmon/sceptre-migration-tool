'''
Created on Nov 29, 2017

@author: Omer Azmon
'''

from sceptre_migration_tool.reverse_resolver import ReverseResolver


class ReverseExports(ReverseResolver):

    def __init__(self, *args, **kwargs):
        super(ReverseExports, self).__init__(*args, **kwargs)
        self._exports = None

    def precendence(self):
        return 10

    def suggest(self, value):
        if self._exports is None:
            self._exports = self._get_exports()
        return self._exports[value] if value in self._exports else None

    def _get_exports(self):
        """
        Communicates with AWS Cloudformation to fetch exports.

        :returns: A formatted version of the stack exports.
        :rtype: dict
        """
        self.logger.debug("Collecting exports...")
        exports = {}
        list_exports_kwargs = {}
        while True:
            response = self.connection_manager.call(
                service="cloudformation",
                command="list_exports",
                kwargs=list_exports_kwargs
            )
            for export in response["Exports"]:
                if export["Value"] in exports:
                    self.logger.warning(
                        "Skipping %s export reverse lookup."
                        " Duplicate Value=%s",
                        export["Name"],
                        export["Value"]
                    )
                else:
                    key = export["Value"]
                    export_key = export["Name"]
                    exports[key] = '!stack_export ' + export_key
            if 'NextToken' in response \
                    and response['NextToken'] is not None:
                list_exports_kwargs = {'NextToken': response['NextToken']}
            else:
                break

        self.logger.debug("Exports: {0}".format(exports))
        return exports