======================
Sceptre Migration Tool
======================

.. image:: https://circleci.com/gh/intuit/sceptre_migration_tool.png?style=shield

About
-----

Sceptre Migration Tool is a tool to assist importing from AWS `CloudFormation <https://aws.amazon.com/cloudformation/>` into a Sceptre environment_. It automates away some of the more mundane, repetitive and error-prone migration tasks.

Features:

- Import single or a set of AWS Cloudformation from AWS into a sceptre environment


Example
-------

Give how Sceptre organises stacks into environments.  Here, we have an empty environment named ``dev``::

  $ tree
  .
  ├── config
  │   └── dev
  │       └── config.yaml
  └── templates


We can create a import a stack with the ``import-stack`` command. Assuming an existing stack named 'aws-vpc'

  $ sceptre import-stack dev vpc aws-vpc.yaml
  dev/vpc - Importing stack
  dev/vpc - Imported AWS CloudFormation template 'aws-vpc' into 'templates/aws-vpc.yaml'
  dev/vpc - Imported stack config from AWS CloudFormation stack 'aws-vpc'
  dev/vpc - Stack imported


We can create a import a complete environment. Assuming two stacks in AWS named 'aws-vpc' and 'aws-subnets'

  $ sceptre import-env dev
  dev - Importing environment
  dev/aws-vpc - Imported AWS CloudFormation template into 'templates/aws-import/aws-vpc.yaml'
  dev/aws-subnets - Imported AWS CloudFormation template into 'templates/aws-import/aws-subnets.yaml'
  dev - Environment imported



Usage
-----

Sceptre Migration Tools can be used from the CLI, or imported as a Python package.

CLI::

  Usage: sceptre_migration_tool [OPTIONS] COMMAND [ARGS]...

    Implements sceptre_migration_tool's CLI.

    Options:
      --version             Show the version and exit.
      --debug               Turn on debug logging.
      --dir TEXT            Specify sceptre_migration_tool directory.
      --output [yaml|json]  The formatting style for command output.
      --no-colour           Turn off output colouring.
      --var TEXT            A variable to template into config files.
      --var-file FILENAME   A YAML file of variables to template into config
                            files.
      --help                Show this message and exit.

    Commands:
      import-env    Import a Sceptre environment from a set of...
      import-stack  Import a Sceptre stack from AWS...


Python:

.. code-block:: python

  from sceptre.environment import Environment
  from sceptre_migration_tool import migrator

  env = Environment("/path/to/sceptre_dir", "environment_name")
  migrator.import_stack(
    env,
    "aws_stack_name",
    "target_sceptre_stack_name",
    "target_template_path"
  )

A full API description of the sceptre migration tool package can be found in the `Documentation <docs/index.html>`__.


Install
-------

::

  $ pip install sceptre_migration_tool

More information on installing sceptre migration tool can be found in our `Installation Guide <docs/install.html>`_.


Tutorial and Documentation
--------------------------

- `Get Started <docs/get_started.html>`_
- `Documentation <docs/index.html>`__


Contributions
-------------

See our `Contributing Guide <CONTRIBUTING.rst>`_.
