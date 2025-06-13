import orjson
import datetime
import uuid
import os

class Makro:
    def __init__(self, name: str, description: str, commands: list[str], json_path: str | None = None) -> None:
        self.name = name
        self.description = description
        self.commands = commands
        self.json_path = json_path if json_path else "No path specified."

        self.created = datetime.datetime.now()
        self.id = uuid.uuid4()
    
    def save(self) -> Bool:
        if not os.path.exists(self.json_path):
            with open(self.json_path, "w") as f:
                f.write("[]")

        with open(self.json_path, "wb") as f:
            f.write(orjson.dumps(self.get_dict))

        return True

    
    def get_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,    
            "commands": self.commands,
            "json_path_save": self.json_path,
            "created": self.created,
            "id": self.id
        }
