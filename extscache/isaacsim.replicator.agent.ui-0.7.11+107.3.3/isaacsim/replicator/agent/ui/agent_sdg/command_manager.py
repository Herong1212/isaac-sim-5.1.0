from __future__ import annotations


class CharacterCommandManager:
    """
    Singleton helper class to handle character command displaying format
    """

    __instance: CharacterCommandManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of CharacterCommandManager is allowed")
        self.name_commands_dict = {}
        self.queue_commands = []  # Store queue declear commands
        self.selected_character = None
        self.is_dirty = False
        CharacterCommandManager.__instance = self

    def get_commands_list(self):
        if self.name_commands_dict is None:
            return None
        commands_list = self.queue_commands.copy()  # Queue command stay on top
        for characterCommands in self.name_commands_dict.values():
            for cmd in characterCommands:
                commands_list.append(cmd)
        return commands_list

    def set_commands_to_agent(self, character_name, command_list):
        if character_name not in self.name_commands_dict.keys():
            return
        self.name_commands_dict[character_name] = command_list
        self.is_dirty = True

    def get_commands_by_name(self, character_name):
        if self.name_commands_dict is None:
            return None

        if character_name not in self.name_commands_dict.keys():
            return None

        return self.name_commands_dict[character_name]

    def get_selected_agent_command(self):
        if self.selected_character is None:
            return None
        return self.get_commands_by_name(str(self.selected_character))

    def set_selected_agent_command(self, command_list):
        if self.selected_character is None:
            return
        self.set_commands_to_agent(self.selected_character, command_list)

    def set_selected_agent_command_without_name(self, command_list):
        if self.selected_character is None:
            return
        # Append character name back to command
        commands_with_name = []
        for cmd in command_list:
            if self.selected_character:
                commands_with_name.append(self.selected_character + " " + cmd)
        self.set_selected_agent_command(commands_with_name)

    def get_selected_agent_command_without_name(self):
        commands = self.get_selected_agent_command()
        # Remove character name (before the first space) from command
        commands_without_name = []
        if commands:
            for cmd in commands:
                commands_without_name.append(cmd[cmd.find(" ") + 1 :])
        return commands_without_name

    def get_agent_list(self):
        if self.name_commands_dict == {} or self.name_commands_dict == None:
            return []

        return self.name_commands_dict.keys()

    def set_commands(self, command_list):
        self.name_commands_dict.clear()
        self.queue_commands.clear()
        if command_list:
            for cmd in command_list:
                if not cmd.strip():  # Skip empty lines
                    continue
                if cmd.startswith("#"):  # Skip comment blocks
                    continue
                name = cmd.split(" ")[0]
                if name == "Queue" or name == "Queue_Spot":
                    self.queue_commands.append(cmd)
                    continue
                if name not in self.name_commands_dict:
                    self.name_commands_dict[name] = []
                self.name_commands_dict[name].append(cmd)
        self.is_dirty = True

    def clear(self):
        self.name_commands_dict = {}
        self.queue_commands = []
        self.selected_character = None

    def set_selected_agent(self, character_name):
        self.selected_character = character_name

    def destroy(self):
        CharacterCommandManager.__instance = None

    @classmethod
    def get_instance(cls) -> CharacterCommandManager:
        if cls.__instance is None:
            CharacterCommandManager()
        return cls.__instance


class RobotCommandManager:
    """
    Singleton helper class to handle robot command displaying format
    """

    __instance: RobotCommandManager = None

    def __init__(self):
        if self.__instance is not None:
            raise RuntimeError("Only one instance of RobotCommandManager is allowed")
        self.name_commands_dict = {}
        self.selected_robot = None
        RobotCommandManager.__instance = self

    def get_commands_list(self):
        if self.name_commands_dict is None:
            return None
        commands_list = []
        for robotCommands in self.name_commands_dict.values():
            for cmd in robotCommands:
                commands_list.append(cmd)
        return commands_list

    def set_commands_to_agent(self, robot_name, command_list):
        if robot_name not in self.name_commands_dict.keys():
            return
        self.name_commands_dict[robot_name] = command_list

    def get_commands_by_name(self, robot_name):
        if self.name_commands_dict is None:
            return None

        if robot_name not in self.name_commands_dict.keys():
            return None

        return self.name_commands_dict[robot_name]

    def get_selected_agent_command(self):
        if self.selected_robot is None:
            return None
        return self.get_commands_by_name(str(self.selected_robot))

    def set_selected_agent_command(self, command_list):
        if self.selected_robot is None:
            return
        self.set_commands_to_agent(self.selected_robot, command_list)

    def set_selected_agent_command_without_name(self, command_list):
        if self.selected_robot is None:
            return
        # Append robot name back to command
        commands_with_name = []
        for cmd in command_list:
            if self.selected_robot:
                commands_with_name.append(self.selected_robot + " " + cmd)
        self.set_selected_agent_command(commands_with_name)

    def get_selected_agent_command_without_name(self):
        commands = self.get_selected_agent_command()
        # Remove character name (before the first space) from command
        commands_without_name = []
        if commands:
            for cmd in commands:
                commands_without_name.append(cmd[cmd.find(" ") + 1 :])
        return commands_without_name

    def get_agent_list(self):
        if self.name_commands_dict == {} or self.name_commands_dict == None:
            return []

        return self.name_commands_dict.keys()

    def set_commands(self, command_list):
        self.name_commands_dict.clear()
        if command_list:
            for cmd in command_list:
                name = cmd.split(" ")[0]
                if name not in self.name_commands_dict:
                    self.name_commands_dict[name] = []
                self.name_commands_dict[name].append(cmd)

    def clear(self):
        self.name_commands_dict = {}
        self.selected_robot = None

    def set_selected_agent(self, robot_name):
        self.selected_robot = robot_name

    def destroy(self):
        RobotCommandManager.__instance = None

    @classmethod
    def get_instance(cls) -> RobotCommandManager:
        if cls.__instance is None:
            RobotCommandManager()
        return cls.__instance
