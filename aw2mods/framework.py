from abc import ABC, abstractmethod
from colorama import init, Back, Style
import struct

class Rom(object):
    def __init__(self, rom_file):
        # type: (str) -> None
        with open(rom_file, 'rb') as f:
            content = f.read()
            self.bites = list(content)

    def read_raw(self, position, length):
        # type: (int, int) -> List[int]
        return self.bites[position: position+length]

    def read(self, position, length):
        return bytes(self.bites[position: position+length])
        
    def write(self, position, value):
        # type: (int, bytes) -> None
        self.bites[position: position + len(value)] = list(value)
    
    def export(self, output_path):
        # type: (str) -> None
        with open(output_path, 'wb+') as f:
            f.write(bytes(self.bites))

class Data(ABC):
    """
    Data represents a chunk of memory within the ROM.
    """

    def __init__(self, position, parent, comment=""):
        self._position = position
        self._parent = parent
        self.comment = comment

    @abstractmethod
    def get_size(self):
        raise NotImplementedError()

    def get_position(self):
        # type: () -> int
        if isinstance(self._parent, Data):
            return self._position +  self._parent.get_position()
        elif isinstance(self._parent, Rom):
            return self._position

        return ValueError('Parent is neither Data nor Rom')

    def get_rom(self):
        if isinstance(self._parent, Rom):
            return self._parent

        if isinstance(self._parent, Data):
            return self._parent.get_rom()

        return ValueError('Parent is neither Data nor Rom')

    def fill(self, byte):
        """Fill the entire struct with the same byte"""
        assert len(byte) == 1
        self.get_rom().write(self.get_position(), byte * self.get_size())



class Type(Data):
    """
    A Type is a specific data type that is readable and writeable
    """

    def __init__(self, position, parent, endian='<', comment=""):
        super().__init__(position, parent)
        self.endian = endian
        self.comment = comment

    def __str__(self):
        return str(self.read())

    @abstractmethod
    def read(self):
        raise NotImplementedError()

    @abstractmethod
    def write(self, value):
        raise NotImplementedError()


class PackedType(Type, ABC):

    @abstractmethod
    def format_string_char(self):
        raise NotImplementedError()

    def format_string(self):
        return "{}{}".format(self.endian, self.format_string_char())

    def read(self):
        return int(struct.unpack(
            self.format_string(),
            self.get_rom().read(self.get_position(), self.get_size())
        )[0])

    def write(self, value):
        value = struct.pack(self.format_string(), value)
        self.get_rom().write(self.get_position(), value)


class UInt8(PackedType):
    def get_size(self):
        return 1

    def format_string_char(self):
        return "B"


class Bool(PackedType):
    def get_size(self):
        return 1

    def format_string_char(self):
        return "?"


class UInt16(PackedType):
    
    def get_size(self):
        return 2
    
    def format_string_char(self):
        return "H"


class UInt32(PackedType):

    def get_size(self):
        return 4

    def format_string_char(self):
        return "I"


class Char(UInt8):

    def read(self):
        return chr(super().read())

    def write(self, value):
        super().write(ord(value))


class Pointer(PackedType):

    GBA_POINTER_OFFSET = 0x8000000
    NULL_PTR = 0 - GBA_POINTER_OFFSET

    def __init__(self, type, position, parent, endian="<", comment=""):
        super().__init__(position, parent, endian, comment)
        self.type = type

    def get_size(self):
        return 4

    def format_string_char(self):
        return "I"

    def read(self):
        return super().read() - self.GBA_POINTER_OFFSET

    def write(self, value):
        super().write(value + self.GBA_POINTER_OFFSET)

    def dereference(self):
        if self.read() == self.NULL_PTR:
            raise Exception("Null Pointer Exception")
        return self.type(self.read(), self.get_rom())

    def __str__(self):
        if self.read() == self.NULL_PTR:
            return "Pointer -> NULL"
        return "Pointer {} -> {}".format(hex(self.read()), str(self.dereference()))


class FixedLengthString(Type):

    def __init__(self, length, position, parent, endian="<", comment=""):
        super().__init__(position, parent, endian=endian, comment=comment)
        self.length = length

    def get_size(self):
        return self.length

    def read(self):
        # TODO probably a better way to do this
        char = Char(0, self)
        result = []
        while char.read() != '\x00':
            result.append(char.read())
            char._position += 1
        return 'FixedLengthString: ({}) "{}"'.format(hex(self._position), ''.join(result))

    def write(self, value):
        if len(value) > self.length - 1:
            raise Exception("Trying to write value that is too big")

        char = Char(0, self)
        for c in value:
            # TODO probably a better way to do this
            char.write(c)
            char._position += 1

        char.write('\x00')

    @staticmethod
    def of_size(size):
        """Factory function to create a string of a certain size
        returns a callable"""
        def create_string_function(*args, **kwargs):
            return FixedLengthString(size, *args, **kwargs)

        return create_string_function


class DynamicString(Type):
    """A string is a null terminated array of chars"""

    @staticmethod
    def size(cls):
        raise RuntimeError("Cannot call size() on a dynamic sized string")

    def read(self):
        char = Char(0, self)
        result = []
        while char.read() != '\x00':
            result.append(char.read())
            char._position += 1
        return ''.join(result)

    def write(self, value):
        pass


class ArrayIndex(UInt16):
    """An ArrayIndex is an index into an array with predefined location

    This is a weird one. Not sure I like it.
    """
    def __init__(self,
                 position,
                 parent,
                 pointer_type,
                 array_start,
                 endian="<",
                 comment="",
                 index_offset=0 # This is used when I have no idea where the start of the array is
                 ):
        self.pointer_type = pointer_type
        self.array_start = array_start
        self.index_offset = index_offset
        super().__init__(position, parent, endian, comment)

    def write(self):
        raise NotImplementedError()

    def dereference(self):
        offset = super().read()
        value = self.pointer_type(0, self.get_rom())
        value._position = self.array_start + (offset+self.index_offset) * value.get_size()
        return value

    def __str__(self):
        return "ArrayIndex [{}] -> {}".format(self.read(), str(self.dereference()))


class Struct(Data):
    """
    A struct is a contiguous chunk of memory at a partcular offset, with a predefined size.
    A structs position is relative to its parents, which may themselves be structs
    A struct has multiple members, which may be structs themselves
    Structs allow you to read data, and access members
    """

    # Used for colorizing display when printing hex values
    COLOR_PALETTE = [Back.RED, Back.YELLOW, Back.GREEN, Back.BLUE, Back.WHITE, Back.CYAN, Back.MAGENTA]

    def get_size(self):
        if not self.members():
            return 0

        sorted_members = sorted(self.members().values(), key=lambda x: x._position)
        return sorted_members[-1]._position + sorted_members[-1].get_size()

    def members(self):
        return {k: v for k, v in vars(self).items() if k != '_parent' and isinstance(v, Data)}


    def display(self, show_members=True, show_hex=True):
        init() # colorama init
        members = sorted([(v, k) for k,v in self.members().items()], key=lambda x: x[0]._position)
        if show_hex:
            print("Raw Bytes:")
            bites = self.get_rom().read(self.get_position(), self.get_size())
            mi = 0

            color = ""
            for i, b in enumerate(bites):
                if mi < len(members) and i == members[mi][0]._position:
                    # If we are at the start of a new member, start printing color
                    color = self.COLOR_PALETTE[mi % len(self.COLOR_PALETTE)]
                    print(color, end='')

                end = '' # The characters to print after printing each byte
                if (i + 1) % 16 == 0:
                    # At the end of a line, end the color, print a new line, then restart the color
                    end = "{}\n{}".format(Style.RESET_ALL, color)

                elif (i+ 1) % 2 == 0:
                    # At the end of a hex pair, print a space
                    end = ' '
                if mi < len(members):
                    # if we are at the end of a member, revert color
                    if i == members[mi][0]._position + members[mi][0].get_size() - 1:
                        end = Style.RESET_ALL + end
                        mi += 1

                print(hex(b)[2:].zfill(2), end=end)

            print(Style.RESET_ALL)

        if show_members:
            print("Members:")

            for i, m in enumerate(members):
                m, name = m
                c = self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]
                print("{}  {} {}: {} {}".format(c, Style.RESET_ALL ,name, str(m), "({})".format(m.comment) if m.comment else ""))

    def __str__(self):
        return "{} (size: {})".format(self.__class__, self.get_size())

