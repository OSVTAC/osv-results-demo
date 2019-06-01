#
# Open Source Voting Results Demo (ORD) - election results report demo
# Copyright (C) 2019  Chris Jerdonek
#
# This file is part of Open Source Voting Results Demo (ORD).
#
# ORD is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""
Script to generate the demo pages.

This requires Python 3.6.

Usage:

    $ python generate.py

"""

import argparse
import logging
import os
from pathlib import Path
import shlex
import subprocess
from textwrap import dedent

import orr


_log = logging.getLogger(__name__)

DESCRIPTION = """\
Build the demo pages.
"""


def get_repo_root():
    return Path(__file__).parent


def get_orr_submodule_dir(repo_root):
    return repo_root / 'submodules/osv-results-reporter/'


def get_input_dirs(repo_root, dir_name, results_dir_name=None):
    """
    Return: (input_dir, input_results_dir).

    Args:
      dir_name: the name of the subdirectory inside "submodules/osv-sample-data"
        to use for the input data.
      results_dir_name: an optional subdirectory name inside the
        "out-orr" directory, which will be used to construct the value
        to pass as --input-results-dir.
    """
    input_dir = repo_root / 'submodules/osv-sample-data' / dir_name / 'out-orr'

    if results_dir_name is None:
        input_results_dir = None
    else:
        input_results_dir = input_dir / results_dir_name

    return (input_dir, input_results_dir)


def get_current_orr_dir():
    """
    Return the path to where orr is located.
    """
    return Path(orr.__file__).parent


def check_current_orr(orr_dir):
    """
    Perform a sanity check on the currently-installed orr.

    Args:
      orr_dir: the directory to use as the ORR repo root, as a Path object.
    """
    current_orr_dir = get_current_orr_dir()
    submodule_orr_dir = (orr_dir / 'src/orr').resolve()
    if current_orr_dir != submodule_orr_dir:
        msg = dedent(f"""\
        The `orr` you have currently installed appears to be different
        from the orr in the submodule of this repository:

          installed_orr: {current_orr_dir}
          submodule_orr: {submodule_orr_dir}
        """)
        # TODO: prompt the user instead?
        _log.warning(msg)


def get_common_args(repo_root, orr_dir, dir_name, results_dir_name=None):
    input_dir = get_input_dirs(repo_root, dir_name)
    input_dir, input_results_dir = get_input_dirs(repo_root, dir_name, results_dir_name=results_dir_name)

    template_dir = orr_dir / 'templates/test-minimal'
    extra_template_dir = template_dir / 'extra'

    args = [
        '--input-dir', input_dir,
        '--template-dir', template_dir,
        '--extra-template-dirs', extra_template_dir,
        '--output-parent',  'docs',
        '--output-subdir', dir_name,
    ]
    if input_results_dir is not None:
        args.extend(('--input-results-dir', input_results_dir))

    return args


def build_election(repo_root, orr_dir, dir_name, results_dir_name=None,
    no_docker=False):
    """
    Args:
      orr_dir: the directory to use as the ORR repo root.
      dir_name: the name of the subdirectory inside "submodules/osv-sample-data"
        to use for the input data.
      results_dir_name: an optional subdirectory name inside the
        "out-orr" directory, which will be used to construct the value
        to pass as --input-results-dir.
    """
    common_args = get_common_args(repo_root, orr_dir, dir_name=dir_name,
                        results_dir_name=results_dir_name)
    # Enable verbose logging.
    orr_args = ['-v']

    if no_docker:
        args = ['orr'] + orr_args + common_args
        print(' '.join(str(a) for a in args))
    else:
        args = ['orr-docker'] + common_args
        args.extend([
            '--source-dir', orr_dir,
            # TODO: expose this as a command-line option?
            # '--skip-docker-build',
            '--orr',
        ])
        args += orr_args

    cmd = ' '.join(shlex.quote(str(arg)) for arg in args)
    msg = dedent(f"""\
    running command:
        $ {cmd}
    """)
    _log.info(msg)

    subprocess.run(args, check=True)


def parse_args(orr_submodule_dir):
    """
    Parse sys.argv and return a Namespace object.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                    formatter_class=argparse.RawDescriptionHelpFormatter)

    orr_dir_help = dedent(f"""\
    an option to force-specify the directory to the ORR repository to use.
    In particular, this directory contains the Dockerfile to use to build.
    Not specifying this will result in using: {orr_submodule_dir} .
    """)
    parser.add_argument('--orr-dir', metavar='DIR', help=orr_dir_help,
        default=orr_submodule_dir)
    parser.add_argument('--no-docker', action='store_true',
        help='suppress using Docker.')

    ns = parser.parse_args()

    return ns


def main():
    repo_root = get_repo_root()
    orr_submodule_dir = get_orr_submodule_dir(repo_root)
    ns = parse_args(orr_submodule_dir)

    log_format = '{asctime} [{levelname}] {msg}'
    logging.basicConfig(level=logging.INFO, format=log_format, style='{',
        datefmt='%Y-%m-%d %H:%M:%S')

    orr_dir = Path(ns.orr_dir)
    no_docker = ns.no_docker

    # Warn the user if they are using an orr different from what is expected.
    check_current_orr(orr_dir)

    input_info = [
        ('2018-06-05', None),
        ('2018-11-06', None),
        # Generate "zero reports" for the Nov. 2018 election.
        ('2018-11-06', 'resultdata-zero'),
    ]

    for input_dir_name, input_results_dir_name in input_info:
        build_election(repo_root, orr_dir=orr_dir, dir_name=input_dir_name,
                       results_dir_name=input_results_dir_name,
                       no_docker=no_docker)


if __name__ == '__main__':
    main()
