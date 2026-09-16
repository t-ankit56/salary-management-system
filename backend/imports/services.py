from typing import BinaryIO


class RosterUploadError(Exception):
    def __init__(self, errors: list[dict]):
        self.errors = errors
        super().__init__("Roster upload validation failed")


def import_roster(file: BinaryIO) -> dict:
    pass
