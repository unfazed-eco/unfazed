import os
import sys
import warnings

from unfazed.core import Unfazed


def get_application() -> Unfazed:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault("UNFAZED_SETTINGS_MODULE", "entry.settings")
    try:
        from unfazed.core import Unfazed
    except ImportError:
        warnings.warn(
            "Could not import unfazed. Did you forget to install it?", stacklevel=2
        )
        sys.exit(1)

    try:
        unfazed = Unfazed()

    except Exception as e:
        warnings.warn(f"An error occurred when init unfazed: {e}", stacklevel=2)
        sys.exit(1)

    return unfazed


application = get_application()
