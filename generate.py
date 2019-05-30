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


def build_election(repo_root, orr_dir, dir_name, results_dir_name=None):
    """
    Args:
      orr_dir: the directory to use as the ORR repo root.
      dir_name: the name of the subdirectory inside "submodules/osv-sample-data"
        to use for the input data.
      results_dir_name: an optional subdirectory name inside the
        "out-orr" directory, which will be used to construct the value
        to pass as --input-results-dir.
    """
    input_dir = get_input_dirs(repo_root, dir_name)
    input_dir, input_results_dir = get_input_dirs(repo_root, dir_name, results_dir_name=results_dir_name)

    template_dir = orr_dir / 'templates/test-minimal'
    extra_template_dir = template_dir / 'extra'

    args = [
        'orr-docker',
        '--input-dir', input_dir,
        '--template-dir', template_dir,
        '--extra-template-dirs', extra_template_dir,
        '--output-parent',  'docs',
        '--output-subdir', dir_name,
        '--source-dir', orr_dir,
        # TODO: expose this as a command-line option?
        # '--skip-docker-build',
    ]
    if input_results_dir is not None:
        args.extend(('--input-results-dir', input_results_dir))
    args.extend(['--orr', '-v'])
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
    Not specifying this will result using: {orr_submodule_dir} .
    """)
    parser.add_argument('--orr-dir', metavar='DIR', help=orr_dir_help,
        default=orr_submodule_dir)

    ns = parser.parse_args()

    return ns


def main():
    repo_root = get_repo_root()
    orr_submodule_dir = get_orr_submodule_dir(repo_root)
    ns = parse_args(orr_submodule_dir)

    logging.basicConfig(level=logging.INFO)

    orr_dir = Path(ns.orr_dir)

    input_info = [
        ('2018-06-05', None),
        ('2018-11-06', None),
        ('2018-11-06', 'resultdata-zero'),
    ]

    # Warn the user if they are using an orr different from what is expected.
    check_current_orr(orr_dir)

    for input_dir_name, input_results_dir_name in input_info:
        build_election(repo_root, orr_dir=orr_dir, dir_name=input_dir_name,
                       results_dir_name=input_results_dir_name)


if __name__ == '__main__':
    main()
