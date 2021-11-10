# -*- mode:python; coding:utf-8 -*-

import os

from ilcli import Command

from iamvcd import __version__ as version
from iamvcd.iam_config import import_iam_user, integrate_vcd_with_iam


class IntegrateOrg(Command):
    """Enable/Refresh IBM Cloud IAM access in a vCD organization."""
    name = 'integrate'

    def _run(self, args):
        org = os.getenv('ORG_ADMIN_USR', '').rsplit('@', 1).pop() or 'N/A'
        vcd = os.getenv('VCD_ROOT', '')
        vcd_short = vcd.split('.', 1)[0].split('//', 1).pop() or 'N/A'
        self.out(f'IAM integration with {vcd_short}/{org} - Started...')
        integrate_vcd_with_iam()
        self.out(f'IAM integration with {vcd_short}/{org} - Finished')


class ImportUser(Command):
    """Import IBM Cloud IAM users into a vCD organization."""
    name = 'import'

    def _init_arguments(self):
        self.add_argument(
            '--user',
            help='IAM user to import into vCD organization',
            metavar='iam_user@foo.com',
            required=True
        )

    def _run(self, args):
        org = os.getenv('ORG_ADMIN_USR', '').rsplit('@', 1).pop() or 'N/A'
        vcd = os.getenv('VCD_ROOT', '')
        vcd_short = vcd.split('.', 1)[0].split('//', 1).pop() or 'N/A'
        self.out(f'Importing {args.user} to {vcd_short}/{org} - Started...')
        import_iam_user(args.user)
        self.out(f'Importing {args.user} to {vcd_short}/{org} - Finished')


class IAMvCD(Command):
    """IAM integration with vCD (command line interface)."""
    subcommands = [IntegrateOrg, ImportUser]

    def _init_arguments(self):
        self.add_argument(
            '--version',
            help='the IAM to vCD integration CLI version',
            action='version',
            version=f'v{version}'
        )


def run():
    iam_vcd = IAMvCD()
    exit(iam_vcd.run())


if __name__ == '__main__':
    run()
