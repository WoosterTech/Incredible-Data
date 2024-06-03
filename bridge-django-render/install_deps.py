# [Generated by Bridge]
import os
import subprocess


def install_dependencies():
    # Check for requirements.txt and install using pip
    if os.path.exists("requirements.txt"):
        print("requirements.txt found. Installing dependencies...")
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)

    # Check for Pipfile.lock and install using Pipenv
    elif os.path.exists("Pipfile.lock"):
        print("Pipfile.lock found. Installing Pipenv and dependencies...")
        subprocess.run(["pip", "install", "pipx"], check=True)
        subprocess.run(["pipx", "install", "pipenv"], check=True)
        subprocess.run(["pipenv", "sync"], check=True)

    # Check for poetry.lock and install using Poetry
    elif os.path.exists("poetry.lock"):
        print("poetry.lock found. Installing Poetry and dependencies...")
        subprocess.run(["pip", "install", "pipx"], check=True)
        subprocess.run(["pipx", "install", "poetry"], check=True)
        subprocess.run(["poetry", "install"], check=True)

    else:
        print(
            "No dependency file found."
            " Please make sure you have a"
            " requirements.txt, Pipfile.lock, or poetry.lock file in the root of your project"
        )


if __name__ == "__main__":
    install_dependencies()
