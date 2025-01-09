import asyncio
import os
import sys
import traceback
import warnings


async def main() -> None:
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
        await unfazed.setup()

    except Exception as e:
        print(traceback.format_exc())
        warnings.warn(f"An error occurred when init unfazed: {e}", stacklevel=2)
        sys.exit(1)

    await unfazed.execute_command_from_argv()


if __name__ == "__main__":
    asyncio.run(main())
