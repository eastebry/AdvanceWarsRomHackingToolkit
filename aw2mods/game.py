from aw2mods.framework import (
    Rom,
    Patch,
    Uint16,
    UInt8
)

class Unit(Patch):
    def __init__(self, position, parent):
        super().__init__(position, parent)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.price = Uint16(14, self)
        self.movement = UInt8(18, self)
        self.max_ammo = UInt8(19, self)
        self.vision = UInt8(20, self)
        self.max_fuel = UInt8(21, self)
    
    def __str__(self):
        return "Unit: price: {}".format(self.price)

class AdvanceWarsTwo(Rom):
    def __init__(self, rom_file):
        super().__init__(rom_file)

        # https://forums.warsworldnews.com/viewtopic.php?t=4
        self.infantry = Unit(0x5D5B10, self)
        # self.mech = Unit(0x5d5b64, self)
        self.mdtank = Unit(0x5d5bc8, self)
        self.tank = Unit(0x5d5c88, self)
        self.recon = Unit(0x5d5cdc, self)
        self.apc = Unit(0x5d5d38, self)
        self.neotank = Unit(0x5d5d94, self)
        self.artillery = Unit(0x5d5e54, self)
        self.rockets = Unit(0x5d5ea8, self)
        self.antiair = Unit(0x5d5fc4, self)
        self.missiles = Unit(0x5d56018, self)
        self.fighter = Unit(0x005d6074, self)
        self.bomber = Unit(0x5d60d0, self)
        self.battlecopter = Unit(0x5d6190, self)
        self.tcopter = Unit(0x5d61e4, self)
        self.battleship = Unit(0x5d6240, self)
        self.cruiser = Unit(0x5d629C, self)
        self.lander = Unit(0x5d62f8, self)
        self.sub = Unit(0x5d6354, self)