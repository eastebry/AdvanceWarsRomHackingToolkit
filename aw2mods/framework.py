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

class Struct(ABC):
    """
    A struct is a contiguous chunk of memory at a partcular offset, with a predefined size.
    A structs position is relative to its parents, which may themselves be structs
    A struct has multiple members, which may be structs themselves
    Structs allow you to read data, and access members
    """

    # Used for colorizing display when printing hex values
    COLOR_PALETTE = [Back.RED, Back.YELLOW, Back.GREEN, Back.BLUE, Back.WHITE, Back.CYAN, Back.MAGENTA]
    
    def __init__(self, position, parent, comment=""):
        self.position = position
        self.parent = parent
        self.comment = comment

    @abstractmethod
    def get_size(self):
        raise NotImplementedError()

    def get_offset(self):
        # type: () -> int
        if isinstance(self.parent, Struct):
            return self.position +  self.parent.get_offset()
        elif isinstance(self.parent, Rom):
            return self.position
        
        return ValueError('Parent is neither patch nor rom')

    def get_rom(self):
        if isinstance(self.parent, Rom):
            return self.parent

        if isinstance(self.parent, Struct):
            return self.parent.get_rom()

        return ValueError('Parent is neither patch nor rom')

    def members(self):
        return {k: v for k, v in vars(self).items() if k != 'parent' and isinstance(v, Struct)}

    def display(self, color=True):
        init() # colorama init
        print("Raw Bytes:")
        bites = self.get_rom().read(self.position, self.get_size())
        members = sorted([(v, k) for k,v in self.members().items()], key=lambda x: x[0].position)
        mi = 0

        for i, b in enumerate(bites):
            if color:
                if i == members[mi][0].position:
                    print(self.COLOR_PALETTE[mi % len(self.COLOR_PALETTE)], end='')
            end = '\n' if (i % 15 == 0 and i != 0) else ' ' if i % 2 == 1 else ''
            if color:
                if i == members[mi][0].position + members[mi][0].get_size() - 1:
                    end = Style.RESET_ALL + end
                    mi += 1
            print(hex(b)[2:].zfill(2), end=end)

        print(Style.RESET_ALL)
        print("Members:")

        for i, m in enumerate(members):
            m, name = m
            c = self.COLOR_PALETTE[i % len(self.COLOR_PALETTE)]
            print("{}  {} {} ({} -> {}): {} {}".format(c, Style.RESET_ALL ,name, hex(m.position), hex(m.position + m.get_size() - 1), m.read(), m.comment))

    def __str__(self):
        return "{} (size: {})".format(self.__class__, self.get_size())


class Type(Struct, ABC):
    """
    A Type is a specific data type that is readable and writeable
    """

    def __init__(self, position, parent, endian='<', comment=""):
        super().__init__(position, parent)
        self.endian = endian
        self.comment = comment

    @abstractmethod
    def format_string_char(self):
        raise NotImplementedError()

    def format_string(self):
        return "{}{}".format(self.endian, self.format_string_char())

    def __str__(self):
        return str(self.read())

    def read(self):
        return int(struct.unpack(
            self.format_string(),
            self.get_rom().read(self.get_offset(), self.get_size())
        )[0])
    
    def write(self, value):
        value = struct.pack(self.format_string(), value)
        self.get_rom().write(self.get_offset(), value)

class UInt8(Type):
    def get_size(self):
        return 1

    def format_string_char(self):
        return "B"

class UInt16(Type):
    
    def get_size(self):
        return 2
    
    def format_string_char(self):
        return "H"

class Char(UInt8):

    def read(self):
        return chr(super().read())

    def write(self, value):
        super().write(ord(value))

class FixedLengthString(Type):

    def __init__(self, length, position, parent, endian="<", comment=""):
        super().__init__(position, parent, endian=endian, comment=comment)
        self.length = length

    def get_size(self):
        return self.length

    def format_string_char(self):
        # TODO it doesn't make sense for this to inherit this method
        raise NotImplementedError()

    def read(self):
        char = Char(0, self)
        result = []
        while char.read() != '\x00':
            result.append(char.read())
            char.position += 1
        return 'FixedLengthString: ({}) "{}"'.format(hex(self.position), ''.join(result))

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
            char.position += 1
        return ''.join(result)

class ArrayIndex(UInt16):
    """An ArrayIndex is an index into an array with predefined location"""
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

    def read(self):
        offset = super().read()
        value = self.pointer_type(0, self.get_rom())
        value.position = self.array_start + (offset+self.index_offset) * value.get_size()
        return "ArrayIndex(val: {} ) -> {}".format(offset, value.read())


