
import sys
from textwrap import dedent

from io import StringIO
from tempfile import TemporaryDirectory
from os.path import join
from re import sub

from rover import init_log
from rover.args import RoverArgumentParser, DEFAULT_LOGVERBOSITY, DEFAULT_VERBOSITY


def log_all(log):
    log.debug('debug')
    log.info('info')
    log.warn('warn')
    log.error('error')
    log.critical('critical')

def remove_timestamp(text):
    return sub(r'\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2},\d{3}', '[timestamp]', text)


def do_all_levels(log_level, log_expected, stdout_level, stdout_expected):

    with TemporaryDirectory() as dir:

        logdir = join(dir, '.rover')
        argparse = RoverArgumentParser()
        args = argparse.parse_args(['--log-dir', logdir, '--log-verbosity', str(log_level), '--verbosity', str(stdout_level)])
        assert args.log_dir == logdir
        assert args.log_verbosity == log_level
        assert args.verbosity == stdout_level

        stdout = StringIO()
        log = init_log(args, 'rover', stdout=stdout)
        log_all(log)
        stdout.seek(0)
        stdout_contents = stdout.read()
        assert stdout_contents == stdout_expected, stdout_contents

        with open(join(logdir, 'rover.log'), 'r') as output:
            log_contents = remove_timestamp(output.read())
            log_expected = remove_timestamp(log_expected)
            assert log_contents == log_expected, log_contents


def test_default_levels():
    do_all_levels(DEFAULT_LOGVERBOSITY,
'''INFO     [timestamp]: info
WARNING  [timestamp]: warn
ERROR    [timestamp]: error
CRITICAL [timestamp]: critical
''',
                  DEFAULT_VERBOSITY,
'''rover  WARNING: warn
rover    ERROR: error
rover CRITICAL: critical
''')

def test_all_levels():
    do_all_levels(5,
'''DEBUG    [timestamp]: debug
INFO     [timestamp]: info
WARNING  [timestamp]: warn
ERROR    [timestamp]: error
CRITICAL [timestamp]: critical
''',
                  5,
'''rover    DEBUG: debug
rover     INFO: info
rover  WARNING: warn
rover    ERROR: error
rover CRITICAL: critical
''')
