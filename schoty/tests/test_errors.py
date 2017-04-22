
import os
import tempfile
from pathlib import Path
import shutil

import pytest

from schoty.base import GitMonoRepo
from schoty.tests.base import _create_repo, TEST_CONFIG

def test_not_existing_repo():
    new_dir = Path(tempfile.mkdtemp())
    try:
        with pytest.raises(RuntimeError):
            mr = GitMonoRepo.clone(['test'],
                                   new_dir / 'monorepo-test',
                                   config=TEST_CONFIG)
    finally:
        if 'SCHOTY_KEEP_TEST_DATA' not in os.environ:
            shutil.rmtree(new_dir)
