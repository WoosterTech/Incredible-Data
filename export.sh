#!/bin/bash

# Function to check if Poetry is installed
check_poetry_installed() {
    if ! command -v poetry &> /dev/null; then
        echo "Poetry is not installed. Please install it and try again."
        exit 1
    fi
}

# Function to export dependencies with Poetry
export_dependencies() {
    # Optional parameter: --dev for exporting only dev dependencies
    local option=$1

    if [[ $option != "--prod" ]] && [[ $option != "--dev-binary" ]]; then
        echo "Exporting development dependencies using Poetry..."
        poetry export --with dev,test,c -f requirements.txt -o ./requirements/local.txt
    fi

    if [[ $option == "--dev-binary" ]]; then
        echo "Exporting non-C development dependencies using Poetry..."
        poetry export --with dev,test,binary -f requirements.txt -o ./requirements/local.txt
    fi

    if [[ $option !== "--dev" ]] && [[ $option != "--dev-binary" ]]; then
        echo "Exporting production dependencies using Poetry..."
        poetry export --with production,c -f requirements.txt -o ./requirements/production.txt
    fi
}

# Check if Poetry is installed
check_poetry_installed

# Get the optional parameter if provided
environment=$1


# Run the appropriate export command based on the parameter
export_dependencies "$environment"
