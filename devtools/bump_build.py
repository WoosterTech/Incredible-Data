import re
import subprocess
from enum import StrEnum
from pathlib import Path
from typing import ClassVar, Self

from pydantic import BaseModel

PROJECT_BASE_PATH = Path(__file__).parent.parent / "incredible_data"

VERSION_FILE = PROJECT_BASE_PATH / "__init__.py"
BUILD_INFO_FILE = PROJECT_BASE_PATH / "build_info.py"

assert VERSION_FILE.exists(), "Version file does not exist, check the path"


def bump_build():
    text = VERSION_FILE.read_text()
    value_pattern = r"__build__\s*=\s*(\d+)"
    match = re.search(value_pattern, text)

    if not match:
        msg = "Could not find __build__ in version file"
        raise ValueError(msg)

    build_number = int(match.group(1)) + 1

    replace_pattern = r"(__build__\s*=\s*)(\d+)"
    new_text = re.sub(replace_pattern, rf"\1{build_number}", text)

    _ = VERSION_FILE.write_text(new_text)


class GitCommand(StrEnum):
    REV_LIST = "rev-list"
    REV_PARSE = "rev-parse"


def git_output(command: GitCommand, *options: str, commit: str = "HEAD") -> str:
    result = subprocess.check_output(  # noqa: S603
        ["git", command, *options, commit],  # noqa: S607
        stderr=subprocess.DEVNULL,
    )
    return result.decode("utf-8").strip()


class GitInfo(BaseModel):
    commit_count: int
    commit_hash: str

    build_number_variable_name: ClassVar[str] = "BUILD_NUMBER"
    commit_hash_variable_name: ClassVar[str] = "COMMIT_HASH"

    @classmethod
    def get_info(cls) -> Self:
        try:
            commit_count = git_output(GitCommand.REV_LIST, "--count")
            commit_hash = git_output(GitCommand.REV_PARSE, "--short")
            return cls(commit_count=commit_count, commit_hash=commit_hash)  # pyright: ignore[reportArgumentType]
        except subprocess.CalledProcessError:
            msg = "Failed to get git info, is git installed?"
            raise RuntimeError(msg) from None

    def write_file(self, file_path: Path) -> None:
        content = (
            f'BUILD_NUMBER = {self.commit_count}\nCOMMIT_HASH = "{self.commit_hash}"\n'
        )
        _ = file_path.write_text(content)

    @classmethod
    def _build_build_number_pattern(cls) -> "re.Pattern[str]":
        return re.compile(rf"{cls.build_number_variable_name}\s*=\s*(\d+)")

    @classmethod
    def _build_commit_hash_pattern(cls) -> "re.Pattern[str]":
        return re.compile(rf"{cls.commit_hash_variable_name}\s*=\s*\"([0-9a-f]+)\"")

    @classmethod
    def from_file(cls, file_path: Path) -> Self:
        content = file_path.read_text()
        build_number_pattern = cls._build_build_number_pattern()
        build_number_matches = build_number_pattern.search(content)
        commit_hash_pattern = cls._build_commit_hash_pattern()
        commit_hash_matches = commit_hash_pattern.search(content)

        if not build_number_matches or not commit_hash_matches:
            msg = "Failed to parse build info file"
            raise ValueError(msg)

        build_number = int(build_number_matches.group(1))
        commit_hash = commit_hash_matches.group(1)

        return cls(commit_count=build_number, commit_hash=commit_hash)


def _stage_file(file_path: Path) -> None:
    file_path_str = str(file_path)
    _ = subprocess.run(["git", "add", file_path_str], check=False)  # noqa: S603, S607


def update_build_info():
    git_info = GitInfo.get_info()
    git_info.write_file(BUILD_INFO_FILE)
    _stage_file(BUILD_INFO_FILE)


if __name__ == "__main__":
    update_build_info()
