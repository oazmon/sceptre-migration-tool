---
layout: docs
---

# Terminology

The following terms will be used though the rest of the Sceptre documentation:

- **Environment Path**: A slash ('/') separated list of directory names which details how to move from the top level config directory to an environment directory. For example, with the following directory structure, the environment path would simply be `dev`:

    ```
    .
    └── config
        └── dev
            ├── config.yaml
            └── vpc.yaml
    ```


  In the following directory structure, the environment path would be `account-1/dev/eu-west-1`:

    ```
    .
    └── config
        └── account-1
            └── dev
                └── eu-west-1
                    ├── config.yaml
                    └── vpc.yaml
    ```

- **Import**: In the context of Sceptre Migration Tool commands, `import` means to create a Sceptre stack config file and template file from an AWS existing stack.
- **Sceptre Directory**: The directory which stores the top level config directory.
