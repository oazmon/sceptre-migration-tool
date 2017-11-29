---
layout: docs
---

# Command Line Interface

Sceptre Migration Tool can be used as a command line tool. Sceptre Migration Tool commands take the format:

```
$ sceptre_migration_tool [GLOBAL_OPTIONS] COMMAND [ARGS] [COMMAND_OPTIONS]
```

Running sceptre migration tool without a subcommand will display help, showing a list of the available commands.

## Global Options

- `--debug`: Turn on debug logging.
- `--dir`: Specify the sceptre directory with an absolute or relative path.
- `--var`: Overwrite an arbitrary config item. For more information, see the section on [Templating]({{ site.baseurl }}/docs/environment_config.html#templating).
- `--var-file`: Overwrite arbitrary config item(s) with data from a variables file. For more information, see the section on [Templating]({{ site.baseurl }}/docs/environment_config.html#templating).


## Commands

The available commands are:

```
$ sceptre_migration_tool import-env
$ sceptre_migration_tool import-stack
```


## Command Options

Command options differ depending on the command, and can be found by running:

```shell
$ sceptre_migration_tool COMMAND --help
```
