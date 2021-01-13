import aw2mods

from argparse import ArgumentParser


def main(in_rom, out_rom):
    # This example shows how to modify the transport properties of a Unit
    #
    # Units have a `transport_pointer` property, which is pointer to a TransportMatrix struct
    # TransportMatrix struct define how many units can be carried, which can be carried, and where
    # they can be unloaded.
    # There are currently three TransportMatrix structs in the ROM: one for landers, tcopters, and APCs
    #
    # Let's start by loading the ROM:

    game = aw2mods.AdvanceWarsTwoExtended(in_rom)

    # Now, let's make it so that APCs can carry two units, instead of 1
    #
    # Two is actually the max capacity. Any more, and the units will disappear.
    #
    # We access the TransportMatrix struct by dereferencing the unit's `transport_pointer`

    game.units.apc.transport_pointer.dereference().capacity.write(2)

    # Now, let's make a unit that previously couldn't carry units into a transport unit.
    #
    # Let's make Bombers work just like tcopters, by setting both of their `transport_pointers` to
    # the same TransportMatrix.

    game.units.bomber.transport_pointer.write(game.units.tcopter.transport_pointer.read())

    # Now, let's do something weird. Let's make it so that tcopters can carry subs.
    #
    # To do this, we change the `sub` property of tcopters TransportMatrix to `True`
    #
    # This will not change _where_ tcopters can load and unload. They will still only be able to
    # load subs over land or buildings, meaning that subs can only be loaded into a tcopter that is
    # on top of a port

    game.units.tcopter.transport_pointer.dereference().sub.write(True)

    # Now, let's make an MdTank carry smaller tanks. We'll call this new tank "MamaTank"
    #
    # Firstly, the MdTank does not currently have a TransportMatrix, and there are no other
    # TransportMatrices that all units to carry _only_ tanks We will have to make a new
    # TransportMatrix in an empty part of the ROM. I've chosen 0x7fff00

    location = 0x7fff00

    # Let's make a new TransportMatrix
    m = aw2mods.TransportMatrix(location, game)

    # Next, zero everything out of the TransportMatrix
    # TODO there should be a helper method for this
    for _, member in m.members().items():
        member.write(0)

    # Set the capacity. MamaTanks will carry two regular tanks
    m.capacity.write(2)

    # Set the TransportMatrix so that the unit can carry tanks
    m.tank.write(True)

    # Set where things can be unloaded
    # I don't totally understand which numbers correspond to which map tiles,
    # so I've just copied the tiles from the APC unit.
    for i in map(lambda x: "land_{}".format(x), (0, 3, 4 ,5, 7, 9, 19, 11, 12, 13, 14, 15, 16, 17, 9)):
        # Allow the unit to unload on this tile
        getattr(m, i).write(True)

    # Lastly, let's set the MdTank's transport pointer to point to our new TransportMatrix!
    game.units.mdtank.transport_pointer.write(location)

    # As a bonus, let's change the MdTank's name to MamaTank
    # This will only change the name on the base's menu, there are some other references to the name
    # That I have not found yet
    game.units.mdtank.name.dereference().write("MamaTank")

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