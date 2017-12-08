'''
Created on Nov 29, 2017

@author: Omer Azmon
'''

from sceptre_migration_tool.reverse_resolvers import ReverseResolver


class ReverseStackOutput(ReverseResolver):

    def __init__(self, *args, **kwargs):
        super(ReverseStackOutput, self).__init__(*args, **kwargs)
        self._stack_output = None
        self._stack_output_external = None

    def precendence(self):
        return 20

    def suggest(self, value):
        if self._stack_output is None:
            self._get_stack_output()

        if value in self._stack_output:
            stack_name, suggestion = self._stack_output[value]
            if stack_name == self.migration_environment.config_path:
                suggestion = None
            self.logger.debug(
                "%s - Internal Stack Suggestion for '%s' is '%s'",
                self.migration_environment.config_path,
                value,
                suggestion
            )
            return suggestion

        if value in self._stack_output_external:
            stack_name, suggestion = self._stack_output_external[value]
            self.logger.debug(
                "%s - External Stack Suggestion for '%s' is '%s'",
                self.migration_environment.config_path,
                value,
                suggestion
            )
            return suggestion

        self.logger.debug(
            "%s - Stack Suggestion for '%s' is 'None'",
            self.migration_environment.config_path,
            value
        )
        return None

    def _get_stack_output(self):
        """
        Communicates with AWS Cloudformation to fetch stack outputs.
        It updates both self._stack_outputs and self._stack_output_external
        with reverse indexes of stack output
        """
        self.logger.debug("Collecting stack outputs...")
        self._stack_output = {}
        self._stack_output_external = {}
        list_stacks_kwargs = {}
        while True:
            response = self.migration_environment.connection_manager.call(
                service="cloudformation",
                command="describe_stacks",
                kwargs=list_stacks_kwargs
            )
            for stack in response["Stacks"]:
                self._build_reverse_lookup(stack)
            if 'NextToken' in response \
                    and response['NextToken'] is not None:
                list_stacks_kwargs = {'NextToken': response['NextToken']}
            else:
                break

        self.logger.debug("Outputs: %s", self._stack_output)
        self.logger.debug("Outputs external: %s", self._stack_output)

    def _build_reverse_lookup(self, stack):
        if 'Outputs' not in stack or not stack['Outputs']:
            return
        #         internal_stack_name = \
        #             self.migration_environment.get_internal_stack(stack['StackName'])
        #         if internal_stack_name:
        #             self._build_internal_stack_lookup(
        #                 internal_stack_name,
        #                 stack['Outputs']
        #             )
        #         else:
        self._build_external_stack_lookup(
            stack['StackName'],
            stack['Outputs']
        )

    def _build_internal_stack_lookup(self, stack_name, outputs):
        for output in outputs:
            self._add_to_reverse_lookup(
                stack_name=stack_name,
                output=output,
                target_dict=self._stack_output,
                resolver_name="stack_output"
            )

    def _build_external_stack_lookup(self, stack_name, outputs):
        for output in outputs:
            self._add_to_reverse_lookup(
                stack_name=stack_name,
                output=output,
                target_dict=self._stack_output_external,
                resolver_name="stack_output_external"
            )

    def _add_to_reverse_lookup(
        self, stack_name, output, target_dict, resolver_name
    ):
        if 'ExportName' in output:
            return
        key = output['OutputKey']
        value = output['OutputValue']
        if value in target_dict:
            self.logger.warning(
                "Skipping %s stack reverse lookup."
                " Duplicate Value: key=%s, value=%s",
                stack_name, key, value
            )
            return
        target_dict[value] = (
            stack_name,
            "!{} '{}::{}'".format(resolver_name, stack_name, key)
        )
