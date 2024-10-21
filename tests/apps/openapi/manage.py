import asyncio
import os
import sys
import warnings


async def main() -> None:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault(
        "UNFAZED_SETTINGS_MODULE", "tests.apps.openapi.backend.settings"
    )
    try:
        from unfazed.core import Unfazed

    except ImportError:
        warnings.warn("Could not import unfazed. Did you forget to install it?")
        sys.exit(1)

    except Exception as e:
        warnings.warn(f"An error occurred: {e}")
        sys.exit(1)

    unfazed = Unfazed()
    await unfazed.setup()
    print(f"routes: {unfazed.router.routes}")
    await unfazed.execute_command_from_argv()


if __name__ == "__main__":
    asyncio.run(main())
