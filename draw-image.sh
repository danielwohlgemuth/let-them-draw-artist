#!/bin/sh
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <shape> <color>"
    exit 1
fi

uv run python utils/test_draw_image.py --shape "$1" --color "$2"