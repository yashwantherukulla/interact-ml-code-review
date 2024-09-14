#!/bin/bash

echo "Current directory: $(pwd)"
echo "Script location: $0"

#path for code review
PROJECT_DIR="/home/talgotram/Repos/interact_hackathonwork/interact-ml-code-review"

cd "$PROJECT_DIR" || { echo "Failed to change to project directory"; exit 1; }

echo "Changed to directory: $(pwd)"

#path for virtual environment
source /home/talgotram/Repos/interact_hackathonwork/interact-ml-code-review/venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

echo "Virtual environment activated"

export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"

echo "Repository URLS: $1"

python -c "from src.__main__ import main; main('$1')"

EXIT_STATUS=$?

deactivate

echo "Virtual environment deactivated"

exit $EXIT_STATUS