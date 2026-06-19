# sitecustomize.py — wird automatisch von Python beim Start geladen
# Fuegt LANGFLOW_COMPONENTS_PATH zu sys.path hinzu, DAMIT
# die lfx.components.minimax Import in model_input_constants.py klappt
import sys, os
for p in os.environ.get("LANGFLOW_COMPONENTS_PATH", "/app/custom_components").split(os.pathsep):
    if p and p not in sys.path:
        sys.path.insert(0, p)
