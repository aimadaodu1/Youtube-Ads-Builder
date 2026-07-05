#!/usr/bin/env bash
python -m playwright install chromium
playwright codegen https://ads.google.com/aw/campaigns/new
