#!/usr/bin/env python
from contextlib import contextmanager
import os.path
import shutil
import sys
import os
from subprocess import call, check_call, check_output
from os.path import abspath, dirname
import glob
from wheel.install import WheelFile
import getpass
import logging
import click


DEFAULT_PYPI_INDEX = 'https://pypi.lundalogik.com:3443/lime/develop'

logger = logging.getLogger(__name__)
ROOT = os.path.abspath(os.path.dirname(__file__))


@click.group(context_settings={'help_option_names': ['--help', '-h']})
@click.option(
    '--loglevel', default='INFO',
    type=click.Choice(['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']))
def cli(loglevel):
    _setup_logger(loglevel)


@cli.command(help='Build package')
def build():
    rm_rf('build')
    rm_rf('dist')
    check_call(['python', 'setup.py', 'bdist_wheel'])


@cli.group(help='Run tests', invoke_without_command=True)
@click.pass_context
def test(ctx):
    if ctx.invoked_subcommand is None:
        ctx.invoke(flake)
        ctx.invoke(test_unit)


@test.command(name='unit', help="Run unit tests")
def test_unit():
    ret = call('py.test', shell=True)
    # return value 5 is "not tests run" in pytest. This is not a error.
    if ret > 0 and not ret == 5:
        raise Exception('Tests failed!')


@test.command(name='coverage', help="Run unit tests and get a coverage report")
def test_coverage():
    rm('.coverage')
    rm_rf('.htmlcov')
    check_call(['coverage', 'run', '-m', 'py.test'])
    check_call(['coverage', 'report',  '-m'])
    check_call(['coverage', 'html', '-d', '.htmlcov', '-i'])
    browse_to('.htmlcov/index.html')


@test.command(help="Check for PEP8 violations")
def flake():
    check_call(['flake8', abspath(dirname(__file__))])


@cli.command(help="Build wheel and upload to internal pypi server")
@click.option('--force', '-f', default=False, is_flag=True, help="Force")
@click.option('--username', '-u', help='Username for uploading to internal '
              'pypi server')
@click.option('--password', '-p', help='Password')
@click.option('--index', '-i', default=DEFAULT_PYPI_INDEX,
              help='Pypi index to use.')
@click.pass_context
def upload(ctx, username=None, password=None, index=DEFAULT_PYPI_INDEX,
           force=False):
    ctx.invoke(build)

    def package_exists(name, version):
        """There needs to be a try catch here because the first time
        a project is uploaded it fails to find the project to check if the
        version exists. Error causes the entire process to stop.

        We assume the error is not network related as if it was other
        erros will be thrown that are not caught.
        """
        exists = False
        try:
            exists = check_output(
                'devpi list {}=={}'.format(name, version).split())
        except Exception:
            return False

        if exists:
            print('Package {}=={} already exists.'.format(name, version))
        return exists

    def get_wheel_path():
        dist_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), 'dist'))
        return next(iter(glob.glob('{}/*.whl'.format(dist_dir))))

    def get_wheel_info(path):
        parsed_filename = WheelFile(path).parsed_filename
        return (parsed_filename.group('name'), parsed_filename.group('ver'))

    if index:
        check_call(['devpi', 'use', index])

    wheel_path = get_wheel_path()
    wheel_name, wheel_version = get_wheel_info(wheel_path)

    if not package_exists(wheel_name, wheel_version) or force:
        if username:
            if not password:
                password = getpass.getpass()
            check_call(['devpi', 'login', username, '--password', password])

        check_call(['devpi', 'upload', wheel_path])
        check_call(['devpi', 'upload', '--no-vcs', '--only-docs'])

        print('Published to pypi: {}=={}'.format(wheel_name, wheel_version))
    else:
        print('Package {}=={} is already published'.format(wheel_name,
                                                           wheel_version))


def rm(path):
    if os.path.isfile(path):
        os.remove(path)


def rm_rf(path):
    if os.path.isdir(path):
        shutil.rmtree(path)


@contextmanager
def cd(path):
    cwd = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(cwd)


def browse_to(filepath):
    filepath = os.path.abspath(filepath)

    if sys.platform.startswith('darwin'):
        call('open', filepath)
    elif os.name == 'nt':
        os.startfile(filepath)
    elif os.name == 'posix':
        call(['xdg-open', filepath])


def _setup_logger(level):
    global_log = logging.getLogger()
    global_log.setLevel(getattr(logging, level))
    global_log.addHandler(logging.StreamHandler(sys.stdout))


if __name__ == '__main__':
    with cd(ROOT):
        cli()
