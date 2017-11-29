---
layout: docs
---

# Get Started

## Install

This tutorial assumes that you have installed Sceptre Migration Tool and Sceptre. Instructions on how to do this are found in the section on [installation]({{ site.url }}{{ site.baseurl }}/docs/install.html).

## Directory Structure

Create the following directory structure in a clean directory named `sceptre-example`:

```shell
.
├── config
│   └── dev
│       ├── config.yaml
└── templates
```

On Unix systems, this can be done with the following commands:

```
$ mkdir config config/dev templates
$ touch config/dev/config.yaml
```

`vpc.json` will contain a CloudFormation template, `vpc.yaml` will contain config relevant to that template, and `config.yaml` will contain environment config.



### config.yaml

Add the following config to `config.yaml`:

```yaml
project_code: sceptre-example
region: us-west-2
```

Sceptre prefixes stack names with the `project_code`. Resources will be built in the AWS region `region`.


## Commands


### Import stack

We can import a stack with the following command by replacing 'aws-stack' with the name of an actual stack in AWS that exists in the region specified above:

```shell
$ sceptre import-stack dev sample aws-stack
```

This command must be run from the `sceptre-examples` directory.


## Next Steps

Further details can be found in the full [documentation]({{ site.url }}{{ site.baseurl }}/docs).
