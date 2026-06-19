#!/bin/bash
# Verify MiniMax provider registration inside the running container.
# Usage: docker exec -it langflow /tmp/verify.sh
#
# Run INSIDE the container. It checks every file we patched
# and tells you what's missing.

set -e
SITE=$(python3 -c "import site; print(site.getsitepackages()[0])")
echo "SITE_PACKAGES: $SITE"
echo "---"

# 1. minimax_constants.py
F="$SITE/lfx/base/models/minimax_constants.py"
if [ -f "$F" ]; then
  echo "OK  minimax_constants.py exists"
  grep -c "MiniMax-M3" "$F" | xargs -I{} echo "    MiniMax-M3 occurrences: {}"
else
  echo "MISSING  $F"
fi

# 2. model_metadata.py
F="$SITE/lfx/base/models/model_metadata.py"
if grep -q '"MiniMax"' "$F" 2>/dev/null; then
  echo "OK  MODEL_PROVIDER_METADATA has MiniMax"
  grep -A1 '"MiniMax":' "$F" | head -3
else
  echo "MISSING  MiniMax entry in MODEL_PROVIDER_METADATA"
fi

# 3. provider_queries.py
F="$SITE/lfx/base/models/unified_models/provider_queries.py"
if grep -q "minimax_constants" "$F" 2>/dev/null; then
  echo "OK  provider_queries.py imports minimax_constants"
  if grep -q "MINIMAX_MODELS_DETAILED" "$F" 2>/dev/null; then
    echo "OK  MINIMAX_MODELS_DETAILED in _STATIC_MODELS_DETAILED"
  else
    echo "MISSING  MINIMAX_MODELS_DETAILED in static list"
  fi
else
  echo "MISSING  minimax import in provider_queries.py"
fi

# 4. model_input_constants.py
F="$SITE/lfx/base/models/model_input_constants.py"
if grep -q "_get_minimax_inputs_and_fields" "$F" 2>/dev/null; then
  echo "OK  _get_minimax_inputs_and_fields() function added"
else
  echo "MISSING  _get_minimax_inputs_and_fields in model_input_constants.py"
fi
if grep -q '"MiniMax"' "$F" 2>/dev/null; then
  echo "OK  MiniMax in MODEL_PROVIDERS_DICT"
else
  echo "MISSING  MiniMax in MODEL_PROVIDERS_DICT"
fi

# 5. Component file
F="$SITE/lfx/components/minimax/minimax.py"
if [ -f "$F" ]; then
  echo "OK  MiniMaxModelComponent at $F"
  grep -c "MiniMax" "$F" | xargs -I{} echo "    MiniMax occurrences: {}"
else
  echo "MISSING  $F"
fi

echo "---"
echo "Live test: get_model_providers() output:"
python3 -c "
from lfx.base.models.unified_models import get_model_providers
print(get_model_providers())
" 2>&1 | head -20
