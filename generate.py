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
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import shlex
import subprocess
import sys
from textwrap import dedent
import time

import orr


_log = logging.getLogger(__name__)


# We use decimal kilobytes (1000) rather than binary (1024).
_KBYTES = 1000

DESCRIPTION = """\
Build the demo pages.
"""

BUILD_DIR = '_build'

MINIMAL_DEMO_INPUT_DIR_NAME = 'minimal-demo'

INDEX_HTML_TEMPLATE = """\
<html>
<head>
  <meta charset="utf-8">
  <title>Results Reporter Demo</title>
</head>
<body>
<h1>Results Reporter Demo</h1>
<p><a href="https://travis-ci.org/OSVTAC/osv-results-demo"><img src="https://travis-ci.org/OSVTAC/osv-results-demo.svg?branch=master" alt="Build Status"/></a>
<p>[Last published on {now}
from Git commit
<a href="https://github.com/OSVTAC/osv-results-demo/commit/{git_sha}"><code>{git_sha}</code></a>.
All built in: {mins} mins and {secs} secs.]
<p>
  This page shows the latest example outputs of the
  <a href="https://osvtac.github.io/">San Francisco Open Source Voting
  System Technical Advisory Committee's</a> (OSVTAC) open source voting
  <a href="https://github.com/OSVTAC/osv-results-reporter">Results Reporter</a>.
<ul>
{items_html}
</ul>
<p>
  File sizes are in decimal kilobytes and megabytes rather than binary.
<p>
  Each hexadecimal string is the
  <a href="https://en.wikipedia.org/wiki/SHA-2">SHA-256</a> hash of the
  listed file. This can be used to check the integrity of the downloaded file.
<p>
  This page is generated from the following OSVTAC GitHub repository:
  <a href="https://github.com/OSVTAC/osv-results-demo">https://github.com/OSVTAC/osv-results-demo</a>.
</body>
</html>
"""


def get_repo_root():
    return Path(__file__).parent


def format_size(size):
    if size < _KBYTES:
        return f'{size} bytes'

    kbytes = size / _KBYTES
    if kbytes < _KBYTES:
        return f'{round(kbytes)} kB'

    mbytes = kbytes / _KBYTES
    return f'{round(mbytes)} MB'


def make_report_item(election_title, rel_home_url, zip_info, output_dir_name, results_title=None):
    """
    Args:
      build_dir: the build directory, as a Path object.
    """
    if results_title is None:
        report_title = election_title
    else:
        report_title = f'[{results_title}] {election_title}'

    rel_zip_path, zip_size, zip_hash = zip_info
    formatted_size = format_size(zip_size)

    html = dedent("""\
    <li>{report_title}
    <ul>
        <li>
            <a href="{home_href}">HTML results</a>
        </li>
        <li><a href="{zip_path}">{zip_file_name}</a>
        ({zip_file_size}) <code>{zip_file_hash}</code>
        </li>
    </ul>
    </li>
    """).format(
        report_title=report_title,
        home_href = str(Path(output_dir_name) / rel_home_url),
        zip_path = str(Path(output_dir_name) / rel_zip_path),
        zip_file_name=Path(rel_zip_path).name,
        zip_file_size=formatted_size,
        zip_file_hash=zip_hash,
    )

    return html


def get_results_title(data):
    results_title = data.get('results_title')
    if results_title is None:
        return None

    try:
        en_results_title = results_title['en']
    except TypeError:
        # TODO: remove this exception handling.
        _log.warn(f'results_title not an internationalized dict: {results_title}')
        return results_title

    return en_results_title


def get_zip_info(data):
    """
    Extract the zip-file related info.

    Returns: (rel_zip_path, zip_size, zip_hash).
    """
    zip_data = data['zip_file']

    return tuple(zip_data[key] for key in ('path', 'bytes', 'hash'))


def make_items_html(reports_data):
    """
    Args:
      reports_data: a list of pairs: (output_dir_name, report_data).
    """
    items = []
    for output_dir_name, data in reports_data:
        try:
            election_title = data['election_title']['en']
            results_title = get_results_title(data)
            rel_home_url = data['rel_home_page']
            zip_info = get_zip_info(data)

            item = make_report_item(election_title, rel_home_url=rel_home_url,
                zip_info=zip_info, output_dir_name=output_dir_name,
                results_title=results_title)
        except:
            raise RuntimeError(f'error while processing output_dir: {output_dir_name}')

        items.append(item)

    return ''.join(items)


def make_index_html_contents(reports_data, git_sha, elapsed_time):
    """
    Args:
      reports_data: a list of pairs: (output_dir_name, report_data).
    """
    items_html = make_items_html(reports_data)

    now = datetime.now()
    # Get the integer hour between 1 and 12 (not padded with zeros).
    hour = int(now.strftime('%I'))
    formatted_now = now.strftime(f'%A, %B {now.day}, %Y at {hour}:%M:%S %p')

    mins, secs = (int(x) for x in divmod(elapsed_time, 60))

    return INDEX_HTML_TEMPLATE.format(
        items_html=items_html, git_sha=git_sha, now=formatted_now, mins=mins, secs=secs
    )


def get_git_sha():
    # Travis's environment variables are documented here:
    # https://docs.travis-ci.com/user/environment-variables/
    sha = os.environ.get('TRAVIS_COMMIT')
    if sha:
        return sha

    # Otherwise, get it manually using Git.
    _log.warning('environment variable "TRAVIS_COMMIT" not found: falling back to Git.')
    args = 'git rev-parse HEAD'.split()
    # Pass encoding so stdout will be str rather than bytes.
    result = subprocess.run(args, stdout=subprocess.PIPE, check=True, encoding='utf-8')
    output = result.stdout.strip()

    return output


def make_index_html(build_dir, reports_data, elapsed_time):
    """
    Args:
      build_dir: the build directory, as a Path object.
      reports_data: a list of pairs: (output_dir_name, report_data).
    """
    git_sha = get_git_sha()

    path = Path(build_dir) / 'index.html'
    text = make_index_html_contents(reports_data, git_sha=git_sha,
                elapsed_time=elapsed_time)

    _log.info(f'writing index.html to: {path}')
    path.write_text(text)


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


def get_common_args(repo_root, orr_dir, input_dir_name, build_dir,
    output_dir_name, results_dir_name=None, skip_pdf=False):
    """
    Args:
      output_dir_name: the name of the subdirectory inside the "docs"
        directory to which to write the output.
      skip_pdf: whether to skip PDF generation.  Defaults to False.
    """
    # We need to special-case the "minimal demo" page.
    if input_dir_name == MINIMAL_DEMO_INPUT_DIR_NAME:
        input_dir = orr_dir / 'sampledata/minimal-test'
        input_results_dir = None
    else:
        input_dir, input_results_dir = get_input_dirs(repo_root, input_dir_name,
            results_dir_name=results_dir_name)

    template_dir = orr_dir / 'templates/demo-template'
    extra_template_dir = template_dir / 'extra'

    args = [
        '--input-dir', input_dir,
        '--template-dir', template_dir,
        '--extra-template-dirs', extra_template_dir,
        '--output-parent', build_dir,
        '--output-subdir', output_dir_name,
        # Enable verbose logging.
        '--verbose',
    ]
    if input_results_dir is not None:
        args.extend(('--input-results-dir', input_results_dir))

    if skip_pdf:
        args.append('--skip-pdf')

    return args


def build_report(repo_root, orr_dir, input_dir_name, build_dir, output_dir_name,
    results_dir_name=None, no_docker=False, delete_okay=False, skip_pdf=False,
    skip_build=False):
    """
    Args:
      orr_dir: the directory to use as the ORR repo root.
      input_dir_name: the name of the subdirectory inside
        "submodules/osv-sample-data" to use for the input data.
      output_dir_name: the name of the subdirectory inside the "docs"
        directory to which to write the output.
      results_dir_name: an optional subdirectory name inside the
        "out-orr" directory, which will be used to construct the value
        to pass as --input-results-dir.
      delete_okay: whether to pass --delete-okay to ORR.
      skip_pdf: whether to skip PDF generation.  Defaults to False.
      skip_build: whether to skip the Docker build.  Defaults to False.
    """
    common_args = get_common_args(repo_root, orr_dir, input_dir_name=input_dir_name,
                        build_dir=build_dir, output_dir_name=output_dir_name,
                        results_dir_name=results_dir_name,
                        skip_pdf=skip_pdf)

    if no_docker:
        args = ['orr'] + common_args
    else:
        args = ['orr-docker'] + common_args
        args.extend(['--source-dir', orr_dir])

    if delete_okay:
        args.append('--delete-okay')

    # TODO: also expose this as a command-line option?
    if skip_build:
        args.append('--skip-docker-build')

    cmd = ' '.join(shlex.quote(str(arg)) for arg in args)
    msg = dedent(f"""\
    running command:
        $ {cmd}
    """)
    _log.info(msg)

    result = subprocess.run(args, stdout=subprocess.PIPE, check=True, encoding='utf-8')
    output = result.stdout

    msg = dedent('''\
    completed command:
        $ {cmd}
    with output:
    """{output}"""
    ''').format(
        cmd=cmd,
        output=output,
    )
    _log.info(msg)

    data = json.loads(output)

    return data


def parse_args(orr_submodule_dir, report_names):
    """
    Parse sys.argv and return a Namespace object.

    Args:
      report_names: a list of the available report names.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION,
                    formatter_class=argparse.RawDescriptionHelpFormatter)

    report_choices = ', '.join(sorted(report_names))
    reports_help = dedent(f"""\
    the name of one or more reports to generate (choose from: {report_choices}).
    Defaults to generating all reports.
    """)
    parser.add_argument('reports', metavar='NAME', nargs='*', help=reports_help)

    orr_dir_help = dedent(f"""\
    an option to force-specify the directory to the ORR repository to use.
    In particular, this directory contains the Dockerfile to use to build.
    Not specifying this will result in using: {orr_submodule_dir} .
    """)
    parser.add_argument('--orr-dir', metavar='DIR', help=orr_dir_help,
        default=orr_submodule_dir)
    parser.add_argument('--no-docker', action='store_true',
        help='suppress using Docker.')
    parser.add_argument('--delete-okay', action='store_true',
        help=('whether to allow directory deletions without prompting.'))
    parser.add_argument('--skip-pdf', action='store_true',
        help='skip PDF generation (useful for testing).')

    ns = parser.parse_args()

    return ns


def main():
    # The `report_name_to_info` dict is the collection of reports
    # available in the demo repo, in the order in which to display them
    # in the index page (Python's dicts preserve insertion ordering).
    #
    # Each key in the dict is the report name (for specifying via
    # the NAME command-line argument, not for display).  We also use the
    # name as the report's `output_dir_name` when building.  Each value
    # in the mapping is a report_info tuple: (input_dir_name, input_results_dir_name).
    report_name_to_info = {
        '2020-03-03': ('2020-03-03/ca/sf', None),
        '2019-11-05': ('2019-11-05', None),
        '2018-11-06': ('2018-11-06', None),
        # Generate "zero reports" for the Nov. 2018 election.
        '2018-11-06-zero': ('2018-11-06', 'resultdata-zero'),
        '2018-06-05': ('2018-06-05', None),
        'minimal-demo': (MINIMAL_DEMO_INPUT_DIR_NAME, None),
    }
    all_report_names = list(report_name_to_info)

    build_dir = BUILD_DIR
    repo_root = get_repo_root()
    orr_submodule_dir = get_orr_submodule_dir(repo_root)
    ns = parse_args(orr_submodule_dir, report_names=all_report_names)

    log_format = '{asctime} [{levelname}] {msg}'
    logging.basicConfig(level=logging.INFO, format=log_format, style='{',
        datefmt='%Y-%m-%d %H:%M:%S')

    report_names = ns.reports
    orr_dir = Path(ns.orr_dir)
    no_docker = ns.no_docker
    delete_okay = ns.delete_okay
    skip_pdf = ns.skip_pdf

    # Warn the user if they are using an orr different from what is expected.
    check_current_orr(orr_dir)

    if not report_names:
        report_names = all_report_names

    try:
        report_infos = [(name, report_name_to_info[name]) for name in report_names]
    except KeyError as exc:
        name = exc.args[0]  # the invalid name
        valid_names = ', '.join(all_report_names)
        msg = f'ERROR: invalid report name: {name!r} (choose from: {valid_names}).'
        print(msg, file=sys.stderr)
        # Return a non-zero exit status to signify an error.
        return 1

    # Compute the total time to do all building.
    start_time = time.time()

    reports_data = []
    skip_build = False
    for report_name, report_info in report_infos:
        # For simplicity, we use the report's "name" for the name of
        # the output directory, as stated in the comments above.
        output_dir_name = report_name
        input_dir_name, input_results_dir_name = report_info

        report_data = build_report(repo_root, orr_dir=orr_dir, input_dir_name=input_dir_name,
            build_dir=build_dir, output_dir_name=output_dir_name,
            results_dir_name=input_results_dir_name, no_docker=no_docker,
            skip_pdf=skip_pdf, delete_okay=delete_okay, skip_build=skip_build)

        reports_data.append((output_dir_name, report_data))
        # We only need to build the first time.
        skip_build = True

    elapsed_time = time.time() - start_time

    make_index_html(build_dir, reports_data, elapsed_time=elapsed_time)


if __name__ == '__main__':
    status = main()
    sys.exit(status)
