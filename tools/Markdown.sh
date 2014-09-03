#!/bin/bash

MARKDOWN=$(dirname ${BASH_SOURCE[0]})/Markdown.pl

for file in $*; do
    echo "Markdown $file"
    basefile=$(basename -s .md $file)
    perl $MARKDOWN $file > ${basefile}.html
done
