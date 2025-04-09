import logging
import typing as t
from pathlib import Path

from tortoise import Tortoise

import unfazed
from unfazed.protocol import DataBaseDriver
from unfazed.schema import AppModels, Command, Database

if t.TYPE_CHECKING:
    from unfazed.core import Unfazed  # pragma: no cover

logger = logging.getLogger(__name__)


class Driver(DataBaseDriver):
    """Tortoise ORM driver implementation for Unfazed framework.

    This driver handles database initialization, migration, and command loading
    for applications using Tortoise ORM.
    """

    AERICH_MODELS = "aerich.models"
    AERICH_COMMAND_LABEL = "aerich.command"
    COMMAND_PATH_TEMPLATE = "unfazed.db.tortoise.commands.{}.Command"

    def __init__(self, unfazed: "Unfazed", conf: Database) -> None:
        """Initialize the Tortoise ORM driver.

        Args:
            unfazed: The Unfazed application instance
            conf: Database configuration

        Raises:
            ConfigurationError: If the database configuration is invalid
        """
        self.conf = conf
        self.unfazed = unfazed
        logger.debug("Initialized Tortoise ORM driver with config: %s", conf)

    async def setup(self) -> None:
        """Set up the database connection and initialize Tortoise ORM.

        This method:
        1. Builds the apps configuration if not provided
        2. Initializes Tortoise ORM with the configuration
        3. Loads Aerich commands for database migrations

        Raises:
            ConfigurationError: If database initialization fails
        """
        # find all models in apps
        if not self.conf.apps:
            self.conf.apps = self.build_apps()

        # init tortoise
        config = self.conf.model_dump(exclude_none=True)
        config.pop("driver")
        await Tortoise.init(config=config)

        # load aerich command
        for c in self.list_aerich_command():
            self.unfazed.command_center.load_command(c)

    async def migrate(self) -> None:
        """Generate database schemas for all registered models.

        This method must be called after setup() to create the necessary
        database tables and schemas.

        Raises:
            ConfigurationError: If schema generation fails
        """
        # must call after setup
        await Tortoise.generate_schemas()

    def build_apps(self) -> t.Dict[str, AppModels]:
        """Build the apps configuration for Tortoise ORM.

        Returns:
            A dictionary containing the models configuration for all registered apps
            and the Aerich models for migrations.
        """
        models_list = [self.AERICH_MODELS]  # support aerich cmd
        for _, app in self.unfazed.app_center:
            if app.has_models():
                models_list.append(f"{app.name}.models")

        return {"models": AppModels(MODELS=models_list)}

    def list_aerich_command(self) -> t.List[Command]:
        """List all available Aerich commands for database migrations.

        Returns:
            A list of Command objects representing available Aerich commands
            found in the internal commands directory.
        """
        internal_command_dir = Path(unfazed.__path__[0] + "/db/tortoise/commands")
        return [
            Command(
                path=self.COMMAND_PATH_TEMPLATE.format(command_file.stem),
                stem=command_file.stem,
                label=self.AERICH_COMMAND_LABEL,
            )
            for command_file in internal_command_dir.glob("*.py")
        ]
