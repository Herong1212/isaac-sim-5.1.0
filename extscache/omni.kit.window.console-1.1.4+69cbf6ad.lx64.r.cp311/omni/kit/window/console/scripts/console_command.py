
from typing import Callable, List, Tuple

import carb
import carb.tokens
import omni.kit.app
import omni.usd

SETTING_LOG_LEVEL = "/persistent/app/extensions/console/filterLevel"
SCIPRT_FOLDER_SETTING= "/app/python/scriptFolders"
AUTOEXEC_LIST_FILE = "autoexec.lst"
EXPECTED_SCRIPT_EXTENSIONS = ["py", "lst"]


def console_log(level: int, message: str):
    # Here is use "console" as module so that message in console window will be short
    carb.log("console", level, "", "", 0, message)


def console_log_info(message: str):
    console_log(carb.logging.LEVEL_INFO, message)


def console_log_warn(message: str):
    console_log(carb.logging.LEVEL_WARN, message)


def console_log_error(message: str):
    console_log(carb.logging.LEVEL_ERROR, message)


class ConsoleCommand:
    def __init__(self, name: str, description: str, function: Callable):
        self.name = name
        self.description = description
        self.function = function


class QuitCommand(ConsoleCommand):
    def __init__(self):
        super().__init__("QUIT", "Quit kit immediately.", self.__quit)

    def __quit(self, *args):
        omni.kit.app.get_app().post_quit()
        return True


class OpenCommand(ConsoleCommand):
    def __init__(self):
        super().__init__("OPEN", "Open a USD file. Followed by the path of the USD file.", self.__open)

    def __open(self, *args):
        if (len(args) == 0):
            console_log_info("OPEN takes a path argument.")
            return False
        
        return omni.usd.get_context().open_stage(args[0]); 


class CloseCommand(ConsoleCommand):
    def __init__(self):
        super().__init__("CLOSE", "Close current USD file.", self.__close)

    def __close(self, *args):
        return omni.usd.get_context().close_stage();


class CommandManager:
    def __init__(self, clear_fn: Callable):
        console_log_info(f"Omniverse Kit Version: {omni.kit.app.get_app().get_build_version()}")

        self.__clear_fn = clear_fn

        self._commands = [
            ConsoleCommand("CLEAR", "Clear console.", self.__on_clear),
            ConsoleCommand("HELP", "Show help.", self.__on_help),
            ConsoleCommand("HISTORY", "List command history.", self.__on_history),
            QuitCommand(),
            OpenCommand(),
            CloseCommand(),
        ]
        self._history_commands = []

        settings = carb.settings.get_settings()
        self._script_folders = settings.get(SCIPRT_FOLDER_SETTING)
        if self._script_folders:
            self._script_folders = [carb.tokens.get_tokens_interface().resolve(folder) for folder in self._script_folders]
            for folder in self._script_folders:
                result, _ = omni.client.stat(folder)
                if result == omni.client.Result.ERROR_NOT_FOUND:
                    omni.client.create_folder(folder)

        # Execute each command that came with --exec
        startup_commands = settings.get("/exts/omni.kit.window.console/startupCommands")
        for command in startup_commands:
            self.execute_command(command)

        result, _ = omni.client.stat(AUTOEXEC_LIST_FILE)
        if result == omni.client.Result.OK:
            self.execute_command(AUTOEXEC_LIST_FILE)

    def execute_command(self, command: str) -> bool:
        """
        Execute command.

        Args:
            command (str): Command string to execute.
        """
        console_log_info(f"# {command}")
        self._history_commands.append(command)
        fields = command.split(" ")
        command = fields[0]
        args = fields[1:]

        for cmd in self._commands:
            if cmd.name == command.upper():
                if cmd.function(*args):
                    return True
                else:
                    console_log_error(f"Command Failed: '{command}'")
                    console_log_error("Type 'HELP' to see help information.")
                    return False
        else:
            if self.execute_file(command, *args):
                return True
            else:   
                return False

    def execute_file(self, script_file: str, *args) -> bool:
        """
        Execute command.

        Args:
            script_file (str): Script file to execute.
            args (list): Arguments to pass to the script.

        Returns:
            True if command is executed successfully, False otherwise.
        """
        if script_file == "":
            return False
        
        fields = script_file.split(".")
        selected_file = None
        selected_postfix = None
        if len(fields) > 1:
            postfix = script_file.split(".")[-1].lower()
            if postfix in EXPECTED_SCRIPT_EXTENSIONS:
                for folder in self._script_folders:
                    result, _ = omni.client.stat(folder + "/" + script_file)
                    if result == omni.client.Result.OK:
                        selected_file = folder + "/" + script_file
                        selected_postfix = postfix
                        break
            else:
                console_log_error(f"Unsupported extension {postfix}")
                return False
        else:
            for folder in self._script_folders:
                for postfix in EXPECTED_SCRIPT_EXTENSIONS:
                    candidate = folder + "/" + script_file + "." + postfix
                    result, _ = omni.client.stat(candidate)
                    if result == omni.client.Result.OK:
                        selected_file = candidate
                        selected_postfix = postfix
                        console_log_info(f"Extension selected to run the file: {selected_file}")
                        break
                if selected_file:
                    break

        if selected_file is None:
            console_log_error(f"Script file '{script_file}' not found.")
            console_log_error(f"Script file should be in [{', '.join(self._script_folders)}].")
            console_log_error(f"Or execute commands in [{', '.join([cmd.name for cmd in self._commands])}].")
            return False

        result, _, content = omni.client.read_file(selected_file)
        if result != omni.client.Result.OK:
            console_log_error(f"Error opening file {selected_file}")

        if selected_postfix == "py":
            omni.kit.app.get_app_interface().get_python_scripting().execute_file(selected_file, args)
            return True
        elif selected_postfix == "lst":
            try:
                for line in memoryview(content).tobytes().decode("utf-8").splitlines():
                    if not self.execute_command(line):
                        return False
                return True
            except Exception as e:
                console_log_error(f"Exception when parsing file {selected_file}: {e}")
            return False
        
        return False

    def list_commands(self, prefix: str) -> List[str]:
        """
        List commands with prefix.

        Args:
            prefix (str): Command prefix.

        Returns:
            Commands list with required prefix.
        """
        candidates = []
        prefix = prefix.upper()
        for cmd in self._commands:
            if cmd.name.startswith(prefix):
                candidates.append(cmd.name)
        for script_file, _ in self._get_scripts():
            if script_file.upper().startswith(prefix):
                candidates.append(script_file)
        candidates.sort()
        return candidates

    def _get_scripts(self) -> List[Tuple[str, str]]:
        scripts = []
        for folder in self._script_folders:
            result, entries = omni.client.list(folder)
            if result == omni.client.Result.OK:
                for entry in entries:
                    if entry.flags & omni.client.ItemFlags.CAN_HAVE_CHILDREN:
                        continue
                    postfix = entry.relative_path.split(".")[-1].lower()
                    if postfix in EXPECTED_SCRIPT_EXTENSIONS:
                        scripts.append((entry.relative_path, folder))
        return scripts

    def __on_clear(self, *args) -> bool:
        if self.__clear_fn:
            self.__clear_fn()

        return True

    def __on_help(self, *args) -> bool:
        settings = carb.settings.get_settings()
        log_level = settings.get(SETTING_LOG_LEVEL) or carb.logging.LEVEL_WARN
        if log_level > carb.logging.LEVEL_INFO:
            console_log_warn("Enable 'Info' log messages to see help information.")

        console_log_info("Commands:")
        for cmd in self._commands:
            console_log_info(f"{cmd.name} - {cmd.description}")

        return True

    def __on_history(self, *args) -> bool:
        for index, cmd in enumerate(self._history_commands):
            console_log_info(f"{index}: {cmd}")

        return True

    

    
