
from os.path import join
from tempfile import TemporaryDirectory
from os import unlink, rmdir

from rover.index import Indexer
from .test_utils import find_root, ingest_and_index


def test_ingest_and_index():
    root = find_root()
    with TemporaryDirectory() as dir:
        config = ingest_and_index(dir, (join(root, 'tests', 'data'),), compact=True, compact_merge=True)
        n = config.db.cursor().execute('select count(*) from tsindex').fetchone()[0]
        assert n == 18, n


def test_deleted_file():
    root = find_root()
    with TemporaryDirectory() as dir:
        config = ingest_and_index(dir, (join(root, 'tests', 'data'),))
        unlink(join(config.args.mseed_dir, 'IU', '2010', '58', 'ANMO.IU.2010.58'))
        indexer = Indexer(config)
        indexer.run([])
        n = config.db.cursor().execute('select count(*) from tsindex').fetchone()[0]
        assert n == 0, n
