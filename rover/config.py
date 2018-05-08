
from genericpath import exists, isfile
from os import unlink
from os.path import basename
from shutil import move

from .args import Arguments
from .logs import init_log
from .sqlite import init_db


class Config:

    def __init__(self):
        argparse = Arguments()
        self.args = argparse.parse_args()
        self.log = init_log(self.args.log_dir, self.args.log_size, self.args.log_count, self.args.log_verbosity,
                            self.args.verbosity, self. args.log_name, self.args.log_unique, self.args.log_unique_expire)
        self.log.debug('Args: %s' % self.args)
        self.db = init_db(self.args.mseed_db, self.log)


def reset_config(config):
    """
    Implement the reset-config command.
    """
    argparse = Arguments()
    file, log = config.args.file, config.log
    if exists(file):
        if not isfile(file):
            raise Exception('"%s" is not a file' % file)
        old = file + "~"
        if not exists(old) or isfile(old):
            log.info('Moving old config file to "%s"' % basename(old))
            if exists(old): unlink(old)
            move(file, old)
        else:
            log.warn('Deleting %s' % file)
            unlink(file)
    log.info('Writing new config file "%s"' % file)
    argparse.write_config(file)