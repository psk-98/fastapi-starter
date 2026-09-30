#!/bin/sh

set -e

cd "$(dirname "$0")/.."

if [ ! -d node_modules ]; then
  echo "installing email dependencies ..."
  bun install
fi

echo "exporting email templates ..."
bun run email:export
