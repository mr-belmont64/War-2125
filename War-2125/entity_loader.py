import json
import color
from entity import Actor #Item
import components.ai as ai
from components.fighter import Fighter

AI_CLASSES = {
    "HostileEnemy": ai.HostileEnemy,
}

class EntityLoader:
    def __init__(self, json_path: str):
        with open(json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def spawn(self, entity_key: str, x: int = 0, y: int = 0):
        if entity_key not in self.data:
            raise ValueError(f"Entity '{entity_key}' not found in JSON data!")

        entry = self.data[entity_key]

        rgb_color = tuple(entry.get("color", [255, 255, 255]))

        if "hp" in entry:
            ai_cls = AI_CLASSES.get(entry.get("ai_type"), ai.HostileEnemy)

            return Actor(
                x=x,
                y=y,
                char=entry["char"],
                color=rgb_color,
                name=entry["name"],
                ai_cls=ai_cls,
                fighter=Fighter(
                    hp=entry["hp"],
                    defense=entry["defense"],
                    power=entry["power"]
                )
            )
        else:
            raise NotImplementedError("Item shit ain't here yet")
            #return Item(
               # x=x,
                #y=y,char=entry["char"],
               # color=rgb_color,
               # name=entry["name"]
            #