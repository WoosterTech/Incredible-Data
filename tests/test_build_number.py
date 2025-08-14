from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from devtools.bump_build import GitInfo, update_build_info

COMMIT_COUNT = 42  # the answer to life, the universe and everything
COMMIT_HASH = "abc123"


@pytest.fixture
def build_info_file(tmp_path: Path) -> Path:
    file_content = f'BUILD_NUMBER = {COMMIT_COUNT}\nCOMMIT_HASH = "{COMMIT_HASH}"\n'
    file_path = tmp_path / "build_info.py"
    _ = file_path.write_text(file_content)
    return file_path


@pytest.fixture
def tmp_build_info_file(tmp_path: Path):
    build_info_file = tmp_path / "build_info.py"
    # Patch BUILD_INFO_FILE to point to our temp file
    with patch("devtools.bump_build.BUILD_INFO_FILE", build_info_file):
        yield build_info_file


@pytest.fixture
def mock_git_info():
    with patch("devtools.bump_build.GitInfo.get_info") as mock_get_info:
        mock_instance = MagicMock(spec=GitInfo)
        mock_instance.commit_count = COMMIT_COUNT
        mock_instance.commit_hash = COMMIT_HASH
        mock_get_info.return_value = mock_instance
        yield mock_instance


def test_from_file_parses_build_info_file(build_info_file: Path):
    git_info = GitInfo.from_file(build_info_file)
    assert git_info.commit_count == COMMIT_COUNT
    assert git_info.commit_hash == COMMIT_HASH


@patch("devtools.bump_build.git_output")
def test_get_info_mocks_git_output(mock_git_output: "MagicMock"):
    # Setup mock return values for commit count and hash
    mock_git_output.side_effect = [f"{COMMIT_COUNT}", COMMIT_HASH]
    info = GitInfo.get_info()
    assert info.commit_count == COMMIT_COUNT
    assert info.commit_hash == COMMIT_HASH


def test_update_build_info_writes_and_stages(
    tmp_build_info_file: Path, mock_git_info: MagicMock
):
    with patch("devtools.bump_build._stage_file") as mock_stage_file:
        update_build_info()
        # Check that write_file was called with the correct path
        mock_git_info.write_file.assert_called_once_with(tmp_build_info_file)  # pyright: ignore[reportAny]
        # Check that _stage_file was called with the correct path
        mock_stage_file.assert_called_once_with(tmp_build_info_file)
