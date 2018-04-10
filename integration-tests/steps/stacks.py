from behave import given, when, then
import time
import os
from botocore.exceptions import ClientError
from sceptre.environment import Environment
from helpers import read_template_file, get_cloudformation_stack_name
from helpers import retry_boto_call


@given('stack "{stack_name}" does not exist')  # noqa: F811
def step_impl(context, stack_name):
    full_name = get_cloudformation_stack_name(context, stack_name)
    status = get_stack_status(context, full_name)
    if status is not None:
        delete_stack(context, full_name)
    status = get_stack_status(context, full_name)
    assert (status is None)


@given('stack "{stack_name}" exists in "{desired_status}" state')  # noqa: F811
def step_impl(context, stack_name, desired_status):
    full_name = get_cloudformation_stack_name(context, stack_name)

    status = get_stack_status(context, full_name)
    if status != desired_status:
        delete_stack(context, full_name)
        if desired_status == "CREATE_COMPLETE":
            body = read_template_file(context, "valid_template.json")
            create_stack(context, full_name, body)
        elif desired_status == "CREATE_FAILED":
            body = read_template_file(context, "invalid_template.json")
            kwargs = {"OnFailure": "DO_NOTHING"}
            create_stack(context, full_name, body, **kwargs)
        elif desired_status == "UPDATE_COMPLETE":
            body = read_template_file(context, "valid_template.json")
            create_stack(context, full_name, body)
            body = read_template_file(context, "updated_template.json")
            update_stack(context, full_name, body)
        elif desired_status == "ROLLBACK_COMPLETE":
            body = read_template_file(context, "invalid_template.json")
            kwargs = {"OnFailure": "ROLLBACK"}
            create_stack(context, full_name, body, **kwargs)

    status = get_stack_status(context, full_name)
    assert (status == desired_status)


@given('stack "{stack_name}" exists using "{template_name}"')  # noqa: F811
def step_impl(context, stack_name, template_name):
    full_name = get_cloudformation_stack_name(context, stack_name)

    status = get_stack_status(context, full_name)
    if status != "CREATE_COMPLETE":
        delete_stack(context, full_name)
        body = read_template_file(context, template_name)
        create_stack(context, full_name, body)

    status = get_stack_status(context, full_name)
    assert (status == "CREATE_COMPLETE")


@given('stack "{stack_name}" does not exist in config')  # noqa: F811
def step_impl(context, stack_name):
    filepath = os.path.join(
        context.sceptre_dir, "config", stack_name + '.yaml'
    )
    os.remove(filepath) if os.path.isfile(filepath) else None


@when('the user imports AWS stack "{aws_stack_name}" into '  # noqa: F811
      'Sceptre stack "{stack_name}" and template "{template_name}"')
def step_impl(context, aws_stack_name, stack_name, template_name):
    full_aws_stack_name = get_cloudformation_stack_name(
        context,
        aws_stack_name
    )
    env = Environment(context.sceptre_dir, os.path.dirname(stack_name))
    stack_base_name = os.path.basename(stack_name)
    context.response = env.import_stack(
        full_aws_stack_name,
        stack_base_name,
        template_name
    )


@then('stack "{stack_name}" exists in "{desired_status}" state')  # noqa: F811
def step_impl(context, stack_name, desired_status):
    full_name = get_cloudformation_stack_name(context, stack_name)
    status = get_stack_status(context, full_name)
    assert (status == desired_status)


@then('stack "{stack_name}" does not exist')  # noqa: F811
def step_impl(context, stack_name):
    full_name = get_cloudformation_stack_name(context, stack_name)
    status = get_stack_status(context, full_name)
    assert (status is None)


@then('stack "{stack_name}" file exists in config')  # noqa: F811
def step_impl(context, stack_name):
    filepath = os.path.join(
        context.sceptre_dir, "config", stack_name + '.yaml'
    )
    assert os.path.exists(
        filepath
    ), "stack '{}' not found at '{}'".format(stack_name, filepath)


def get_stack_status(context, stack_name):
    try:
        stack = retry_boto_call(context.cloudformation.Stack, stack_name)
        retry_boto_call(stack.load)
        return stack.stack_status
    except ClientError as e:
        if e.response['Error']['Code'] == 'ValidationError' \
          and e.response['Error']['Message'].endswith("does not exist"):
            return None
        else:
            raise e


def create_stack(context, stack_name, body, **kwargs):
    retry_boto_call(
        context.client.create_stack,
        StackName=stack_name, TemplateBody=body, **kwargs
    )

    wait_for_final_state(context, stack_name)


def update_stack(context, stack_name, body, **kwargs):
    stack = retry_boto_call(context.cloudformation.Stack, stack_name)
    retry_boto_call(stack.update, TemplateBody=body, **kwargs)

    wait_for_final_state(context, stack_name)


def delete_stack(context, stack_name):
    stack = retry_boto_call(context.cloudformation.Stack, stack_name)
    retry_boto_call(stack.delete)

    waiter = context.client.get_waiter('stack_delete_complete')
    waiter.config.delay = 4
    waiter.config.max_attempts = 240
    waiter.wait(StackName=stack_name)


def wait_for_final_state(context, stack_name):
    stack = retry_boto_call(context.cloudformation.Stack, stack_name)
    delay = 2
    max_retries = 150
    attempts = 0
    while attempts < max_retries:
        retry_boto_call(stack.load)
        if not stack.stack_status.endswith("IN_PROGRESS"):
            return
        attempts += 1
        time.sleep(delay)
    raise Exception("Timeout waiting for stack to reach final state.")
