#!/bin/sh
# Builds the calculator pages and deploys the site to Cloudflare Pages (project paydar-site).
set -e
cd "$(dirname "$0")"
python3 tools/_build.py
rm -rf .dist && mkdir .dist
git ls-files -co --exclude-standard | grep -v -E '^(README.md|deploy.sh|\.gitignore|tools/_build.py)$' | tar -cf - -T - | tar -xf - -C .dist
npx -y wrangler@4 pages deploy .dist --project-name paydar-site --branch main --commit-dirty=true
