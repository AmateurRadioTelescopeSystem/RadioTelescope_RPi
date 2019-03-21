#!/usr/bin/env sh

cd Core/
find . -iname "*.py" | xargs pylint --exit-zero --rcfile="../ci/pylintrc"