import sys
import aw2mods

def main():
    if len(sys.argv) !=3:
        print("Not enough args")
        return
    rom = sys.argv[1]
    game = aw2mods.AdvanceWarsTwoExtended(rom)

    game.units.apc.price.write(400)

    game.units.antitank.price.write(900)

    game.units.mdtank.price.write(1400)

    game.units.heavytank.movement.write(5)
    game.units.heavytank.price.write(1800)

    game.units.lander.price.write(600)

    game.units.battleship.price.write(2400)
    game.units.battleship.max_range.write(5)

    game.units.sub.price.write(1400)
    game.units.sub.max_fuel.write(50)
    game.units.sub.vision.write(4)
    game.units.sub.primary_weapon_damage.destroyer.write(60)

    game.units.destroyer.price.write(600)
    game.units.destroyer.vision.write(3)
    game.units.destroyer.primary_weapon_damage.sub.write(60)
    game.units.destroyer.primary_weapon_damage.battleship.write(60)
    game.units.destroyer.primary_weapon_damage.destroyer.write(60)
    game.units.destroyer.primary_weapon_damage.battlecruiser.write(45)

    game.units.cruiser.vision.write(4)

    game.units.battlecruiser.price.write(2000)
    game.units.battlecruiser.primary_weapon_damage.battleship.write(60)

    game.units.striker.price.write(2000)

    game.units.bomber.price.write(1800)
    game.units.bomber.primary_weapon_damage.battlecopter.write(10)

    game.units.bomber.transport_pointer.write(0x86e80b4)
    game.units.tcopter.transport_pointer.dereference().sub.write(True)
    game.units.lander.transport_pointer.dereference().sub.write(True)
    game.units.apc.transport_pointer.dereference().sub.write(True)

    output = sys.argv[2]
    game.export(output)

    
if __name__ == '__main__':
    main()