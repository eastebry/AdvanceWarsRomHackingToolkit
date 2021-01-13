import json
from aw2mods.framework import (
    Rom,
    Struct,
    UInt16,
    UInt8,
    Bool,
    Pointer,
    Type,
    ArrayIndex,
    FixedLengthString,
)
STRING_TABLE_POSITION = 0x006dda3c

class Unit(Struct):

    def __init__(self, position, parent):
        super().__init__(position, parent)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.name = ArrayIndex(0, self, FixedLengthString.of_size(12), STRING_TABLE_POSITION, index_offset=-2234)
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
        self.transport_pointer = Pointer(TransportMatrix, 20, self, comment="(0x86e8000 = APC, 0x86e812c=Lander, 0x86e80b4=Tcopter)")
        self.unit_class = UInt8(24, self, comment="Not sure what this changes")
        self.movement_type = UInt8(25, self, comment="0=Infantry, 1=Mech, 2=tread, 3=tires, 4=air, 5=ship, 6=lander")
        self.deploy_from = UInt8(26, self, comment="Where to deploy from. 4=Base, 16=Airport, 32=port")
        self.ai_handling = UInt8(27, self)

        self.primary_weapon_damage = DamageMatrix(31, self)
        self.secondary_weapon_damage = DamageMatrix(57, self)

        self.unknown_pointer_1 = Pointer(UInt8, 84, self)
        self.unknown_pointer_2 = Pointer(UInt8, 88, self)

    def read(self):
        return "Unit"

    def __str__(self):
        return json.dumps({k: v.read() for k, v in self.members().items() if isinstance(v, Type)})


class TransportMatrix(Struct):
    """TransportMatrix specifies the transport properties of a unit"""

    def __init__(self, position, parent):
        super().__init__(position, parent)

        self.capacity = UInt8(0, self, comment="Cannot be more than 2")

        for i, name in enumerate(self.get_rom().unit_order()):
            setattr(self, name, Bool(i + 2, self))

        for i in range(31):
            setattr(self, "land_{}".format(i), Bool(27 + i, self))

            # Not sure what these all are


            # Lander can unload on          10                      19
            # APC on        0     3 4 5 7 9 10 11 12 13 14 15 16 17 19
            # Tcopter on    0 1 2 3 4 5 7 9 10 11 12 13 14 15 16 17 19

            # So...
            # 10 = port
            # 19 = Shoal
            # 1 and 2 = probably rivers?


    def read(self):
        return "TransportMatrix"

class DamageMatrix(Struct):
    """DamageMatrix indicates how much damage this unit does against other Units"""

    def __init__(self, position, parent):
        super().__init__(position, parent)
        for i, name in enumerate(list(self.get_rom().unit_order()) + ["dived_sub"]):
            setattr(self, name, UInt8(i, self))

    def read(self):
        return "DamageMatrix"



class AdvanceWarsTwo(Rom):

    def __init__(self, rom_file):
        super().__init__(rom_file)

        # Add all the units
        # Units are stored in contiguous blocks starting at 0x5d5b18
        # Unit description in this forum post:
        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.units = Struct(0x5D5B18, self)
        for index, unit_name in enumerate(self.unit_order()):
            setattr(self.units, unit_name, Unit(index * 92, self.units)) # 92 = Size of Unit struct

    def unit_order(self):
        return ("infantry","mech","mdtank","empty1","tank","recon","apc","neotank","empty2","artillery","rockets","empty3",
                    "empty4","antiair","missiles","fighter","bomber","empty5","battlecopter","tcopter","battleship",
                    "cruiser","lander","sub",)

class AdvanceWarsTwoExtended(AdvanceWarsTwo):
    """This is a class for the ROMhack "Advance wars 2 extended"""
    def __init__(self, rom_file):
        super().__init__(rom_file)

    def unit_order(self):
        return ("infantry","mech","mdtank","antitank","tank","recon","apc","heavytank","patrol","artillery","rockets","striker",
                "destroyer","antiair","missiles","fighter","bomber","battlecruiser","battlecopter","tcopter","battleship",
                "cruiser","lander","sub")
