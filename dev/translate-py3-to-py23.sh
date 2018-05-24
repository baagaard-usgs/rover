#!/bin/bash

source env3/bin/activate

pushd ..
rm -fr rover23
mkdir rover23
cp -r rover/rover rover23
cp -r rover/tests rover23

pushd rover23
pasteurize -w -n --no-diffs .
# make intern work!
sed -i '/from builtins import bytes/d' rover/coverage.py
popd

cp -r rover/docs rover23
cp -r rover/robot rover23
cp rover/setup.py rover23
cp rover/README.md rover23
cp rover/LICENSE rover23

pushd rover23
find . -name "*.pyc" -exec rm \{} \;
find . -name __pycache__ -exec rmdir \{} \;
popd
popd

