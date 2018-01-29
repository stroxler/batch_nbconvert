from tdx.cli import fire_cli

from . import core


class BatchNbConvert:

    def __init__(self):
        # directory-oriented commands
        self.exec_copy = core.exec_copy
        self.strip_copy = core.strip_copy
        self.strip_inplace = core.strip_inplace
        # file-oriented methods
        self.exec_file_inplace = core.exec_file_inplace
        self.exec_file_copy = core.exec_file_copy


def main():
    fire_cli(BatchNbConvert())()
