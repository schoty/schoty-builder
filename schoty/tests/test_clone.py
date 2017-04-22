import os
import tempfile
from pathlib import Path
import shutil

import pytest

from schoty.base import GitMonoRepo
from schoty.tests.base import _create_repo


@pytest.mark.parametrize('n_commits', [1, 2, 4])
def test_create_repo(n_commits):
    new_dir = Path(tempfile.mkdtemp())
    try:
        name_1 = 'test1'
        r1 = _create_repo(new_dir / name_1, n_commits)
    finally:
        if 'SCHOTY_KEEP_TEST_DATA' not in os.environ:
            shutil.rmtree(new_dir)


@pytest.mark.parametrize('shallow', [False, True])
def test_create_monorepo(shallow):
    new_dir = Path(tempfile.mkdtemp())
    try:
        name1 = 'test1'
        name2 = 'test2'

        ur1 = _create_repo(new_dir / name1, n_commits=2)
        ur2 = _create_repo(new_dir / name2, n_commits=3)

        # check non shallow clone
        monorepo_path = new_dir / 'mono-repo-0'

        mr = GitMonoRepo.clone([ur1.base_path.as_uri(),
                                ur2.base_path.as_uri()],
                               monorepo_path,
                               shallow=shallow)
        if shallow:
            for name in [name1, name2]:
                # make sure we have a shallow clone
                assert mr[name].n_commits_ == 1
        else:
            # the cloned repo must exactly match
            assert ur1 == mr[name1]
            assert ur2 == mr[name2]

        # make sure that the new folders are created in the monorepo
        for name in mr:
            assert (mr.base_path / name).exists()
        assert mr.monorepo.n_commits_ == 1

    finally:
        if 'SCHOTY_KEEP_TEST_DATA' not in os.environ:
            shutil.rmtree(new_dir)
