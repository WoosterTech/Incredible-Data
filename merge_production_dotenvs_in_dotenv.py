from collections.abc import Sequence
from pathlib import Path

BASE_DIR = Path(__file__).parent.resolve()
PRODUCTION_DOTENVS_DIR = BASE_DIR / ".envs" / ".production"
PRODUCTION_DOTENV_FILES = [
    PRODUCTION_DOTENVS_DIR / ".django",
    PRODUCTION_DOTENVS_DIR / ".postgres",
]
DOTENV_FILE = BASE_DIR / ".env"


def merge(output_file: Path, files_to_merge: Sequence[Path]) -> None:
    content: list[str] = []
    for file in files_to_merge:
        text = file.read_text()
        # Strip trailing newline to avoid doubling, then add consistent newline
        content.append(text.rstrip("\n"))

    # Join with newlines and add final newline if content exists
    if content and any(content):
        _ = output_file.write_text("\n".join(content) + "\n")
    else:
        _ = output_file.write_text("\n")


if __name__ == "__main__":
    merge(DOTENV_FILE, PRODUCTION_DOTENV_FILES)
