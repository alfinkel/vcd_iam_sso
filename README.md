# vCD and IBM Cloud IAM SSO integration tool

Command line interface for integrating VMware virtual Cloud Director (vCD) with
IBM Cloud Identity and Access Management (IAM) single sign on authentication.

## Overview

This repository provides a command line tool (`iamvcd`) that performs the
rudimentary functions of integrating IBM Cloud IAM SSO authentication with a
vCD organization.
`iamvcd` can be used to:
    - Enable IAM SSO authentication for a vCD organization.
    - Import an IAM user to a vCD organization where IAM SSO authentication has
    been enabled.

## Installation

The following instructions are necessary in order to successfully install,
configure and use the `iamvcd` command line tool.

### Prerequisites

- [Git][git]
- [Python 3.6+][python]
- A basic understanding of Git and Python virtual environments
- An IBM Cloud IAM client id/secret
- The vCD organization administrator username and password.  The username's
format is `admin@<my_organization_name>`.
- The vCD organization's vCD base URL. For example:
`https://daldir04.vmware-solutions.cloud.ibm.com`, the vCD here is `daldir04`.

### Setup

The setup of the reference implementation and accompanying CLI `iamvcd` is
relatively straight forward.  The high level steps are:

- Check out this Github repository with [Git][git] locally.
- Create a Python virtual environment.
- Activate your virtual environment.

```shell
git clone git@github.com:alfinkel/vcd_iam_sso.git
cd vcd_am_sso
python -m venv venv
. ./venv/bin/activate
```

- Install all relevant Python dependencies.
   - This repo requires the following libraries:
      - [PyCryptodome][pycryptodome] - Handles the conversion of IAM
      Identity public RSA keys from JSON Web Key (JWK) to Privacy Enhanced Mail
      (PEM) format.
      - Python [requests][] - Handles the HTTP requests to APIs.
      - [ilcli][] - A thin wrapper around Python's [argparse][] library.
   - Installing dependencies differs slightly if you're an end user or if
   you're a developer interested in making changes to the repo.
      - If you're an end user execute the following:

      ```shell
      make install
      ```

      - If you're a developer execute the following:

      ```shell
      make develop
      ```

### CLI Usage

The general assumptions of this usage section are that your virtual
environment is active and your current directory is this repo's root directory.

#### Priming the environment

The command line interface depends on a handful of configurable operating
system environment variables.  They are listed below:

- `IAM_ROOT`:  The IAM root URL, e.g. `https://iam.cloud.ibm.com` or
`https://iam.test.cloud.ibm.com`.
- `VCD_ROOT`:  The vCD root URL, e.g.
`https://sdaldir04.vmware-solutions.cloud.ibm.com`.
- `ORG_ADMIN_USR`: The specific organization admin user id, e.g.
`admin@test_dcea9c04d6f74d0ca2464887584c28e1`.
- `ORG_ADMIN_PWD`: The specific organization admin user password.
- `IAM_CLIENT_ID`: The IBM Cloud IAM client id.
- `IAM_CLIENT_SECRET`: The IBM Cloud client secret.

The [env_prime.sh][env-prime] script is provided for your convenience and can
be updated and sourced prior to using `iamvcd`.  Once [env_prime.sh][env-prime]
has been updated accordingly you can set the environment variables by executing
the following:

```shell
. ./scripts/env_prime.sh
```

#### Enabling IAM SSO for a vCD organization

To enable IAM SSO for the vCD organization administered by the `ORG_ADMIN_USR`,
use the CLI's `integrate` sub-command and execute the following:

```shell
iamvcd integrate
```

**NOTE**: Use the same command to refresh the IAM Identity public RSA keys
periodically.  The keys are rotated every 30 days so the versions stored for
the vCD organization must be kept current in order to ensure authentication
continues to function.

#### Enabling IAM user SSO authentication

Once IAM SSO has been enabled for a vCD organization you can grant an IAM user
access to that vCD organization by importing that user into the vCD
organization.  To do this, use the CLI's `import` sub-command along with the
user's IAM user ID and execute a command similar to the following:

```shell
iamvcd import --user my.username@ibm.com
```

**NOTE**: Currently importing users is limited to a single user at a time when
using the `iamvcd` CLI.

**Happy authenticating!!**


[git]: https://git-scm.com/downloads
[python]: https://www.python.org/downloads/
[pycryptodome]: https://pycryptodome.readthedocs.io/en/latest/
[requests]: https://docs.python-requests.org/en/latest/
[ilcli]: https://cloudant.github.io/ilcli/
[argparse]: https://docs.python.org/3/library/argparse.html
[env-prime]: https://github.com/alfinkel/vcd_iam_sso/blob/master/scripts/env_prime.sh
