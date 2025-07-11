#!/bin/bash

# Capture the output of git status --porcelain
GIT_STATUS_OUTPUT=$(git status --porcelain)

# Check if the output is empty
if [ -z "$GIT_STATUS_OUTPUT" ]; then
  echo "Git working tree is clean (no uncommitted changes)."
  exit 0
else
  echo "Git working tree has uncommitted changes:"
  echo "$GIT_STATUS_OUTPUT"
  echo "These changes will be pushed to the scratch_chat_dev branch."#main
fi

git add .
git commit -m "[BOT] Update file from workflow"
git push origin scratch_chat_dev #main
