#!/bin/bash
set -e
echo "=== Novel Creation Omnibus Installer ==="
command -v node >/dev/null 2>&1 || { echo "Need Node.js v18+"; exit 1; }
npx skills add limingnanyue/novel-creation-omnibus -g
echo "Done! Try: 帮我写一本小说"
