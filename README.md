# Schoty builder

This package conatains the builder for the schoty project. It proviedes a unifed view for multiple user-repositories and implements a synchronisation mechanism between the monorepo and the individual repositories.

## Installation notes

Schoty builder requires Python 3.6 (mostly to use f-strings) and only supports Linux. It can be installed as follows,

```bash
conda config --append channels conda-forge
conda create --name schoty-env --file requirements.txt python=3.6
source activate schoty-env
python setup.py develop
```


## Related projects
 
  - https://github.com/beberlei/composer-monorepo-plugin
  - https://conda-forge.github.io/ (for the Github integration procedures)
