---
layout: page
---

# About

Sceptre Migration Tool is a tool to import configuration from AWS into Sceptre. Currently, the tool imports AWS Cloudformation scripts.
The tool is accessible as a CLI tool, or as a Python module.


## Motivation

Many teams start creating CloudFormation manually or with other tools and with to migrate to use Sceptre. This could be a delicate process to do manually.
This tool imports the stacks as-is and allow further incremental massaging, to make the process of migration more Robust.

The migration tool was developed separate from Sceptre (it imports Sceptre internally) to reduce the complexity of the core code for what is basically a one time use.


## Overview

The migration tool is used by a relationship between AWS Cloudformation stacks and the corresponding template files and YAML config files in the Sceptre configuration directory tree.

For a tutorial on using Sceptre, see [Get Started](https://sceptre.cloudreach.com/latest/docs/get_started.html).


## Code

Sceptre Migration Tools source code can be found on [Github](https://github.intuit.com/SBSEG-EPIC/sceptre-migration-tool).

Bugs and feature requests should be raised via our [Issues](https://github.intuit.com/SBSEG-EPIC/sceptre-migration-tool/issues) page.
