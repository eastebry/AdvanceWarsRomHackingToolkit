import json
from aw2mods.framework import (
    Rom,
    Struct,
    UInt16,
    UInt8,
    Type,
    RelativePointer,
    Char,
    String
)
STRING_TABLE_POSITION = 0x006dda3c - 2234 # TODO this number is wrong. It does not account for pointer math

class Unit(Struct):

    def __init__(self, position, parent):
        super().__init__(position, parent)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        # TODO this needs to be a fixed string
        self.unit_name = RelativePointer(8, self, String, STRING_TABLE_POSITION)
        #self.unit_name = UInt16(8, self, comment="(Don't understand)")
        self.primary_weapon_index = UInt16(10, self, comment="(Don't understand)")
        self.secondary_weapon_index = UInt16(12, self, comment="(Don't understand)")
        self.price = UInt16(14, self, comment="(Value is one-tenth of the full unit price)")
        self.movement = UInt8(18, self)
        self.max_ammo = UInt8(19, self)
        self.vision = UInt8(20, self)
        self.min_range = UInt8(22, self)
        self.max_range = UInt8(23, self)
        self.max_fuel = UInt8(24, self)
        self.is_direct = UInt8(25, self, comment="(1=direct, 2=indirect)")

    def __str__(self):
        return json.dumps({k: v.read() for k, v in self.members().items() if isinstance(v, Type)})


class AdvanceWarsTwo(Rom):
    def __init__(self, rom_file):
        super().__init__(rom_file)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.infantry = Unit(0x5D5B10, self)
        self.mech = Unit(0x5d5b6c, self)
        self.mdtank = Unit(0x5d5bc8, self)
        self.tank = Unit(0x5d5c80, self)
        self.recon = Unit(0x5d5cdc, self) 
        self.apc = Unit(0x5d5d38, self)
        self.neotank = Unit(0x5d5d94, self)
        self.artillery = Unit(0x5d5e4c, self)
        self.rockets = Unit(0x5d5ea8, self)
        self.antiair = Unit(0x5d5fbc, self)
        self.missiles = Unit(0x5d6018, self)
        self.fighter = Unit(0x005d6074, self)
        self.bomber = Unit(0x5d60d0, self)
        self.battlecopter = Unit(0x5d6188, self)
        self.tcopter = Unit(0x5d61e4, self)
        self.battleship = Unit(0x5d6240, self)
        self.cruiser = Unit(0x5d629C, self)
        self.lander = Unit(0x5d62f8, self)
        self.sub = Unit(0x5d6354, self)

class AdvanceWarsTwoExtended(AdvanceWarsTwo):
    """This is a class for the ROMhack "Advance wars 2 extended"""
    def __init__(self, rom_file):
        super().__init__(rom_file)
        self.heavytank = Unit(0x5d5d94, self)
        self.antitank = Unit(0x5d5c24,self)
        self.battlecruiser = Unit(0x5d612c ,self)
        self.destroyer = Unit(0x5d5f60,self)
        self.striker = Unit(0x5d5f04, self)
        self.neotank = None
