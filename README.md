# AdvanceWars2 Rom Hacking Toolkit
Project to build a better tool for modding the classic GBA game: Advance Wars 2

## Usage
Clone this repository, then open a python3 shell
```python
import aw2mods

# Load the main rom
game = aw2mods.AdvanceWarsTwo('/path/to/advancewars2.gba')

# Change things

# Lets make the infantry unit cost $100 (price is stored as a tenth of the total)
print(game.infantry.price.read()) # Get the current value (outputs 100)
game.infantry.price.write(1) 

# Also make the the Transport Copter move further
print(game.tcopter.movement.read())
game.tcopter.movement.write(8)

# Now save the ROM
game.export('my_patched_rom.gba')
```

## TODO
There's a lot that's not implemented yet. This is very much a work in progress


## Documentation
https://forums.warsworldnews.com/viewtopic.php?f=11&t=11130
COs: https://forums.warsworldnews.com/viewtopic.php?t=5
