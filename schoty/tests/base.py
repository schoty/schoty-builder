from schoty.base import GitRepo
from schoty.utils import _communicate

TEST_CONFIG = {'user.name': 'Schoty',
               'user.email':  'contact@schoty.io'}


def _create_repo(base_path, n_commits=1, config=None):
    name = base_path.name
    r1 = GitRepo._create(base_path, verbose=False,
                         config=config)
    if n_commits >= 1:
        with (r1.base_path / 'README.md').open('w') as fh:
            fh.write('Initial commit\n')
        out1 = r1.add([r1.base_path / 'README.md'])
        assert r1.n_commits_ == 0
        out2 = r1.commit(f'Initial commit ({name})')
    if n_commits >= 2:
        for i_commit in range(1, n_commits):
            with (r1.base_path / 'README.md').open('w') as fh:
                fh.write(f'Commit {i_commit}')
            out = r1.commit(f'Commit {i_commit} ({name})', a=True)

    assert r1.n_commits_ == n_commits
    return r1
