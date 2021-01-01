import sys
import aw2mods

def main():
    if len(sys.argv) !=3:
        print("Not enough args")
        return
    rom = sys.argv[1]
    game = aw2mods.AdvanceWarsTwoExtended(rom)
    game.lander.price.write(600)
    game.battleship.price.write(2400)
    game.battleship.max_range.write(5)
    game.sub.price.write(1400)
    game.sub.max_fuel.write(60)
    game.mdtank.price.write(1400)
    game.heavytank.movement.write(5)
    game.heavytank.price.write(1800)
    game.battlecruiser.price.write(2000)
    game.antitank.price.write(900)

    game.destroyer.price.write(1000)
    game.striker.price.write(2200)

    game.infantry.is_direct.write(2)
    game.infantry.max_range.write(4)
    game.infantry.min_range.write(2)

    game.infantry.display()

    output = sys.argv[2]
    game.export(output)

    
if __name__ == '__main__':
    main()