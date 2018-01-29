import os
import json
import shutil
import glob
import logging
from typing import List
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

import tdx
from plumbum import cmd, local


logger = logging.getLogger(__name__)
MANIFEST_NAME = "nbconvert_manifest.json"


def strip_copy(src_dir: str,
               dst_dir: str,
               parallel: int = 1,
               clobber: bool = False) -> None:
    """
    Copy the code from `src_dir`, and create a fresh git
    repo at `dst_dir` based on it, but with all ipython notebook
    outputs stripped.

    The `parallel` command can be used to strip output in
    parallel, if you have several cores and speed is an issue.
    The `clobber` output controls whether to remove any existing
    content in `dst_dir`
    """
    copy_repo(src_dir, dst_dir, clobber)
    strip_inplace(dst_dir, parallel)


def strip_inplace(directory: str,
                  parallel: int = 1) -> None:
    """
    Strip output from all ipython notebooks within a repo
    in-place.

    The `parallel` command can be used to strip output in
    parallel, if you have several cores and speed is an issue.
    """
    notebooks = _find_notebooks(directory)
    with ThreadPoolExecutor(parallel) as pool:
        list(pool.map(strip_file_inplace, notebooks))


def exec_copy(src_dir: str,
              dst_dir: str,
              parallel: int = 1,
              clobber: bool = False) -> None:
    """
    Given a git repository at `src_dir`, copy all the contents
    to `dst_dir` to make a fresh git repo. Then, run all of the
    ipython notebooks inplace.

    You can think of this as creating a "built" git repo at
    `dst_dir`.

    The `parallel` command can be used to run notebooks in
    parallel, if you have several cores and speed is an issue.
    The `clobber` output controls whether to remove any existing
    content in `dst_dir`
    """
    copy_repo(src_dir, dst_dir, clobber)
    # do the conversion
    notebooks = _find_notebooks(dst_dir)
    with ThreadPoolExecutor(parallel) as pool:
        list(pool.map(lambda nb: exec_file_inplace(nb, 'notebook'),
                      notebooks))
    # save a manifest
    sha = _get_sha(src_dir)
    logger.info(f"Writing manifest indicating sha of {sha}")
    converted = {nb: sha for nb in notebooks}
    tdx.write_json(converted, Path(dst_dir) / MANIFEST_NAME)


def convert_one(notebook: str,
                dst_dir: str):
    "NOTE: not currently used, may be removed"
    git_root, relative_notebook = _git_root_and_relative(notebook)
    destination = _find_and_set_up_dest(relative_notebook, dst_dir)
    exec_file_copy(notebook, destination, 'notebook')
    manifest_path = Path(dst_dir) / MANIFEST_NAME
    manifest = tdx.read_json(manifest_path)
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)


def _find_and_set_up_dest(relative_path, dst_dir):
    absolute_dst = os.path.join(dst_dir, relative_path)
    containing_dir = os.path.dirname(absolute_dst)
    if not os.path.isdir(containing_dir):
        os.makedirs(containing_dir)
    return absolute_dst


# single-file operations

def strip_file_inplace(notebook: str) -> None:
    logger.info(f"Stripping output from {notebook}")
    content = cmd.python['-m', 'nbstripout', notebook]()
    with open(notebook, 'w') as f:
        f.write(content)


def exec_file_copy(notebook: str,
                   destination: str,
                   output_type: str) -> None:
    logger.info(f"Converting {notebook} to {output_type} inplace")
    out = cmd.jupyter['nbconvert', '--execute', '--to', output_type,
                      notebook] > destination
    with open(destination, 'w') as f:
        f.write(out)


def exec_file_inplace(notebook: str,
                      output_type: str) -> None:
    logger.info(f"Converting {notebook} to {output_type} inplace")
    cmd.jupyter['nbconvert', '--execute', '--inplace',
                '--to', output_type,
                notebook]()


def copy_repo(src_dir: str, dst_dir: str, clobber: bool=False):
    _clear_directory(dst_dir, clobber)
    shutil.copytree(src_dir, dst_dir, ignore=_ignore_git_stuff)
    with local.cwd(dst_dir):
        cmd.git["init"]


# utilities

def _find_notebooks(directory: str) -> List[str]:
    return tdx.add_lists(
        glob.glob(f'{directory}/**/*.ipynb'),
        glob.glob(f'{directory}/*.ipynb'),
    )


def _git_root_and_relative(notebook_path: str) -> (str, str):
    nb_dir = os.path.dirname(notebook_path)
    with local.cwd(nb_dir):
        git_root = cmd.git["rev-parse", "--show-toplevel"].strip()
    rel_notebook = os.path.relpath(notebook_path, git_root)
    return git_root, rel_notebook


def _get_sha(directory: str) -> str:
    with local.cwd(directory):
        return cmd.git["rev-parse", "HEAD"]().strip()


def _ignore_git_stuff(src: str, names: List[str]) -> List[str]:
    return [n for n in names if n.startswith('.git')]


def _clear_directory(directory: str,
                     clobber: bool) -> None:
    if os.path.exists(directory):
        if clobber:
            logger.info(f"Removing existing directory {directory}")
            shutil.rmtree(directory)
        else:
            raise ValueError('If `clobber` is not set to True, the '
                             f'target directory {directory} must not '
                             'exist')