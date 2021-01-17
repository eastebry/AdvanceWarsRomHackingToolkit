import aw2mods

from argparse import ArgumentParser


def main(in_rom, out_rom):
    # This example shows how to make basic modifications to a unit
    # First, let's load the ROM.

    game = aw2mods.AdvanceWarsTwo(in_rom)

    # Units are accessible via `game.units`
    # You can use the `display` function to view all the inputs
    # This will show the raw bytes that make up the unit, and which bytes
    # correspond to which properties of the unit

    print("Infantry Unit Details:")
    game.units.infantry.display()

    # Lets start by changing the price of some units
    # Price is stored as 1/10th the actual unit cost

    game.units.apc.price.write(400) # 400 = cost of 4000
    game.units.neotank.price.write(2000)
    game.units.lander.price.write(600)

    # Now, let's change the movement of some units
    # There is a maximum bound, above a certain number the game will break
    game.units.mech.movement.write(4)

    # Change the vision
    game.units.recon.vision.write(6)

    # Change the fuel
    game.units.sub.max_fuel.write(70)

    # Mess with the units' ranges

    # Make bombers indirect by setting their min range to  > 1
    game.units.bomber.min_range.write(2)
    game.units.bomber.max_range.write(6)
    # We will also set the is_direct property, which
    # changes whether or not they can move and shoot in the same turn
    # 1 = direct unit, 2 = indirect unit
    game.units.bomber.is_direct.write(2)

    # Make battleships direct attack units
    game.units.battleship.min_range.write(1)
    game.units.battleship.max_range.write(1)
    game.units.battleship.is_direct.write(1)

    # Allow the mech to attack as a direct
    # or indirect unit, by setting it's max range to 3 and
    # its min range to 1
    game.units.mech.min_range.write(1)
    game.units.mech.max_range.write(3)
    # In this case, setting is_direct makes no difference. "Indirect Mechs"
    # are able to move and shoot in the same turn. I'm not entirely sure why this is,
    # but its likely because has something to do with them having a min range of 1
    # In general, setting units to be both direct and indirect (like we are doing here) has
    # strange behavior
    game.units.mech.is_direct.write(2)

    # Allow the fighter attack indirectly
    # It will be able to move and shoot in the same
    # turn
    game.units.fighter.min_range.write(1)
    game.units.fighter.max_range.write(3)
    game.units.fighter.is_direct.write(1)

    game.units.tcopter.display()

    # Finally, let's save the game
    game.export(out_rom)

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('input_rom', help='Original rom to modify')
    parser.add_argument('output_rom', help='Name of newly created rom')

    args = parser.parse_args()
    if args.input_rom == args.output_rom:
        raise RuntimeError("Input rom and output rom should not be the same file")
    main(args.input_rom, args.output_rom)
