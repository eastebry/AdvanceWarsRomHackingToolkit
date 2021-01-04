import json
from aw2mods.framework import (
    Rom,
    Struct,
    UInt16,
    UInt8,
    UInt32,
    Pointer,
    Type,
    ArrayIndex,
    FixedLengthString,
)
STRING_TABLE_POSITION = 0x006dda3c

class DamageMatrix(Struct):
    """DamageMatrix indicates how much damage this unit does against other Units"""

    def __init__(self, position, parent):
        super().__init__(position, parent)
        for i, name in enumerate(AdvanceWarsTwo.UNIT_ORDER):
            setattr(self, name, UInt8(i, self))

    def read(self):
        return "DamageMatrix"

class Unit(Struct):

    def __init__(self, position, parent):
        super().__init__(position, parent)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.unit_name = ArrayIndex(0, self, FixedLengthString.of_size(12), STRING_TABLE_POSITION, index_offset=-2234)
        self.primary_weapon_index = UInt16(2, self, comment="(Don't understand)")
        self.secondary_weapon_index = UInt16(4, self, comment="(Don't understand)")
        self.price = UInt16(6, self, comment="(Value is one-tenth of the full unit price)")
        self.movement = UInt8(10, self)
        self.max_ammo = UInt8(11, self)
        self.vision = UInt8(12, self)
        self.min_range = UInt8(14, self)
        self.max_range = UInt8(15, self)
        self.max_fuel = UInt8(16, self)
        self.is_direct = UInt8(17, self, comment="This doesn't do what we think it does, but these numbers hold true (1=direct, 2=indirect)")
        self.transport_pointer = Pointer(20, self, comment="(0x86e8000 = APC, 0x86e812c=Lander, 0x86e80b4=Tcopter)")
        self.unit_class = UInt8(24, self, comment="Not sure what this changes")
        self.movement_type = UInt8(25, self, comment="0=Infantry, 1=Mech, 2=tread, 3=tires, 4=air, 5=ship, 6=lander")
        self.deploy_from = UInt8(26, self, comment="Where to deploy from. 4=Base, 16=Airport, 32=port")
        self.ai_handling = UInt8(27, self)

        self.primary_weapon_damage = DamageMatrix(31, self)
        self.secondary_weapon_damage = DamageMatrix(57, self)

        self.unknown_pointer_1 = Pointer(84, self)
        self.unknown_pointer_2 = Pointer(88, self)

    def read(self):
        return "Unit"

    def __str__(self):
        return json.dumps({k: v.read() for k, v in self.members().items() if isinstance(v, Type)})


class AdvanceWarsTwo(Rom):
    UNIT_ORDER=["infantry","mech","mdtank","glitchy1","tank","recons","apc","neotank","glitchy2","artillery","rockets","glitchy3",
                "glitchy4","antiair","missiles","fighter","bombers","glitchy5","battlecopter","tcopter","battleship",
                "cruiser","lander","sub","dived_sub"]

    def __init__(self, rom_file):
        super().__init__(rom_file)

        # Add all the units
        # Units are stored in contiguous blocks starting at 0x5d5b18
        # Unit description in this forum post:
        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.units = Struct(0x5D5B18, self)
        for index, unit_name in enumerate(self.UNIT_ORDER[:-1]): # Enumerate all except dived subs
            setattr(self.units, unit_name, Unit(index * 92, self.units)) # 92 = Size of Unit struct

class AdvanceWarsTwoExtended(AdvanceWarsTwo):
    """This is a class for the ROMhack "Advance wars 2 extended"""
    def __init__(self, rom_file):
        super().__init__(rom_file)
        # TODO
        #self.heavytank = Unit(0x5d5d94, self)
        #self.antitank = Unit(0x5d5c24,self)
        #self.battlecruiser = Unit(0x5d612c ,self)
        #self.destroyer = Unit(0x5d5f60,self)
        #self.striker = Unit(0x5d5f04, self)
        #self.neotank = None
