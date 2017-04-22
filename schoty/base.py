import re
from pathlib import Path
from subprocess import Popen, PIPE
import shutil
import warnings

from schoty.utils import _check_output

GIT_CMD = shutil.which('git')


class GitMonoRepo(dict):
    """Monorepo manager

    Parameters
    ----------
    repos : dict
       a dict with as keys repo names and as vales their path
    base_path : str
       path to the new monorepo
    """

    def __init__(self, base_path):
        if not isinstance(base_path, Path):
            base_path = Path(base_path)
        self.base_path = base_path
        if not base_path.exists():
            raise IOError(f'Monorepo {base_path} does not exists!')
        self.monorepo = GitRepo(self.base_path)

    @classmethod
    def clone(cls, repos, base_path, force=False, verbose=False,
              shallow=True):
        """ Create a new git repository
        (mostly for testing purposes)

        Parameters
        ----------
        repos : list
           a list of repository paths
        base_path : str
          directory where the repository should be created
        force : str
          if the repository already exists, overwrite it
        verbose : str
          print additional progress statements
        shallow : bool
          make a shallow clone

        Returns
        -------
        cls : GitRepo
          the git repository object
        """
        mrepo = GitRepo._create(base_path, force=force, verbose=verbose)

        base_path = mrepo.base_path

        (base_path / '.repos').mkdir()

        mrep = cls(base_path)

        repos_d = {}
        for path in repos:
            name = Path(path).name
            if name.endswith('.git'):
                name = name[:-4]
            if name in repos_d:
                warnings.warn(f'Repository:\n         {path}\n'
                              f'already in the monorepo'
                              f'with the key {name} corresponding to\n'
                              f'         {repos_d[name]}\n'
                              f'and will be ingored!')
            else:
                repos_d[name] = path

        # clone all the upstream repos
        for repo_name, repo_path in repos_d.items():
            mrep[repo_name] = GitRepo.clone(repo_path,
                                            base_path / '.repos' / repo_name,
                                            shallow=shallow)

        # copy all files to the monorepo:
        for repo_name, repo_path in repos_d.items():
            shutil.copytree(mrep[repo_name].base_path, base_path / repo_name)
            shutil.rmtree(base_path / repo_name / '.git')

        # add new files to the repo
        res_add = mrep.monorepo.add(list(repos_d.keys()))
        res = mrep.monorepo.commit(f'Initial commit ({len(repos)} repos)',
                                   a=True)
        if 'files changed' not in res:
            raise ValueError('Creation of the monorepo failed! \n'
                             + res_add + res)

        return mrep


class GitRepo(object):
    """A quick Python wrapper around the git CLI command

    Parameters
    ----------
    base_path : str
       local path to the repository

    Attributes
    ----------
    log_ : str
       the output of the git log command
    n_commits_ : int
       the number of commits in the log
    """

    def __init__(self, base_path):
        if not isinstance(base_path, Path):
            base_path = Path(base_path)
        self.base_path = base_path

        if not base_path.exists():
            raise IOError(f"base_path: {base_path} does not exist!")
        if not (base_path / '.git').exists():
            raise ValueError(f'Not a git repository '
                             f'{base_path}')

    def commit(self, message, a=False):
        """ Make a new commit

        Parameters
        ----------
        message : str
           the commit message
        a : bool
           commit all changed files (`git commit -a` command)
        """
        CMD = [GIT_CMD, "commit", "-m", message]
        if a:
            CMD.insert(2, '-a')
        p = Popen(CMD, cwd=self.base_path.as_posix(),
                  stdout=PIPE, stderr=PIPE)
        return _check_output(p, cmd=CMD)

    def add(self, files):
        """ Call `git add` on the provided files

        Parameters
        ----------
        files : list
            list of file paths
        """
        CMD = [GIT_CMD, "add"]
        CMD += [f'{el}' for el in files]
        p = Popen(CMD, cwd=self.base_path.as_posix(),
                  stdout=PIPE, stderr=PIPE)
        return _check_output(p, cmd=CMD)

    @property
    def log_(self):
        """ Return the log of the current directory"""
        p = Popen([GIT_CMD, "log"], cwd=self.base_path.as_posix(),
                  stdout=PIPE, stderr=PIPE)
        return _check_output(p, cmd=[GIT_CMD, "log"])

    @property
    def n_commits_(self):
        """ Return the number of commits """
        n = 0
        try:
            log = self.log_
            for line in log.splitlines():
                if re.match('^commit\s[0-9a-f]+\s*$', line):
                    n += 1
        except RuntimeError:
            pass

        return n

    @classmethod
    def clone(cls, repo_path, destination_path, force=False, verbose=False,
              shallow=False):
        """ Create a new git repository
        (mostly for testing purposes)

        Parameters
        ----------
        repo_path : str
          url or path to the upstream repo
        destination_path : str
          directory where the repository should be created
        force : str
          if the repository already exists, overwrite it
        verbose : bool
          print additional progress statements
        shallow : bool
          make a shallow clone

        Returns
        -------
        cls : GitRepo
          the git repository object
        """
        base_path = destination_path
        if base_path.exists():
            if force:
                shutil.rmtree(base_path)
            else:
                raise IOError(f'Repository {base_path} '
                              f'already exists. Please use the `force` '
                              'parameter to overwrite')
        if shallow:
            CMD = ['--depth', '1']
        else:
            CMD = []

        CMD = [GIT_CMD, "clone"] + CMD + [repo_path, destination_path]

        p = Popen(CMD, stdout=PIPE, stderr=PIPE)
        outs = _check_output(p, cmd=CMD)
        if verbose:
            print(outs)
        return cls(base_path)

    def __eq__(self, other):
        return self.log_ == other.log_

    @classmethod
    def _create(cls, base_path, force=False, verbose=False):
        """ Create a new git repository
        (mostly for testing purposes)

        Parameters
        ----------
        base_path : str
          directory where the repository should be created
        force : str
          if the repository already exists, overwrite it
        verbose : str
          print additional progress statements

        Returns
        -------
        cls : GitRepo
          the git repository object
        """
        if not isinstance(base_path, Path):
            base_path = Path(base_path)

        if base_path.exists():
            if force:
                shutil.rmtree(base_path)
            else:
                raise IOError(f'Repository {base_path} '
                              f'already exists. Please use the `force` '
                              'parameter to overwrite')

        (base_path).mkdir()

        p = Popen([GIT_CMD, "init"], cwd=base_path.as_posix(),
                  stdout=PIPE, stderr=PIPE)
        outs = _check_output(p)
        if verbose:
            print(outs)
        return cls(base_path)

    def __repr__(self):
        return f"<GitRepo [{self.base_path}]>"
