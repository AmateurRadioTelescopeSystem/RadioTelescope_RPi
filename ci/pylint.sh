#!/usr/bin/env sh

echo -e "\e[1;32mPylint check is running...\e[0m"

cd Core/
find . -iname "*.py" | xargs pylint --exit-zero --rcfile="../ci/pylintrc"