import orjson
import datetime
import uuid
import os

class Makro:
    def __init__(self, name: str, description: str, commands: list[str], json_path: str | None = None, created: str | None = None, id: str | None = None) -> None:
        self.name = name
        self.description = description
        self.commands = commands
        self.json_path = json_path if json_path else "No path specified."

        self.created = datetime.datetime.now() if not created else created
        self.id = uuid.uuid4() if not id else id
    
    def save(self) -> bool:
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
