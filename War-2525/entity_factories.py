from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

player = Actor(
    char="@",
    color=(255, 255, 255,),
    name="Player",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=100, defense=5, power=20)
)

muman = Actor(
    char="M",
    color=(63, 126, 63),
    name="Muman",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=50, defense=4, power=15),
)
mumanscienist = Actor(
    char="M",
    color=(20, 123, 0),
    name="Muman Scienist",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=55, defense=5, power=11)
)
