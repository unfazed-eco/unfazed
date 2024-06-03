from unfazed.core import Unfazed

if __name__ == "__main__":
    app = Unfazed()
    app.setup_cli()

    app.execute_command_from_argv()
