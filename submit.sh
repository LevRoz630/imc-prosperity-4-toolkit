#!/usr/bin/env bash
# Bundle a strategy into a single submission-ready file.
# Usage: ./submit.sh strategies/my_strat.py
#
# Output: submissions/my_strat.py (ready to upload to prosperity.imc.com)
set -e

if [ -z "$1" ]; then
    echo "Usage: ./submit.sh strategies/my_strat.py"
    exit 1
fi

STRAT="$1"
NAME=$(basename "$STRAT")
mkdir -p submissions

# Read logger, strip its imports (we'll add unified imports at top)
LOGGER=$(grep -v "^import \|^from " strategies/logger.py)

# Read strategy, remove local imports and standalone logger= line
STRATEGY=$(grep -v "^from backtester\.\|^from strategies\.\|^logger = Logger()" "$STRAT")

cat > "submissions/$NAME" << PYEOF
import json
from typing import Any
from datamodel import Listing, Observation, Order, OrderDepth, ProsperityEncoder, Symbol, Trade, TradingState

$LOGGER

logger = Logger()

$STRATEGY
PYEOF

echo "Submission ready: submissions/$NAME"
