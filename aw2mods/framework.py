from abc import ABC, abstractmethod
import hashlib
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

    def display(self):
        bites = self.get_rom().read(self.position, self.get_size())
        bites = list(map(lambda x: str(hex(x)[2:]).zfill(2), bites))
        final = []
        for i in range(len(bites)):
            final.append(bites[i])
            if i > 0 and i % 15 == 0:
                final.append("\n")
            elif i % 2 == 1:
                final.append(" ")

        print("-" * 39)
        print("Struct ({} members)".format(len(self.members())))
        print("Position {}, Size {}".format(hex(self.position), self.get_size()))
        print("-" * 39)
        print("0    2    4    6    8    a    c    e")
        print("".join(final))
        print("-" * 39)

        for k, v in self.members().items():
            print("{} ({} -> {}): {} {}".format(k, hex(v.position), hex(v.position + v.get_size() - 1), v.read(), v.comment))
        print("-" * 39)

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

class OffsetPointer(UInt16):
    """A Relative pointer is an offset from a predefined location"""
    def __init__(self,
                 position,
                 parent,
                 pointer_type,
                 offset_from,
                 endian="<",
                 comment="",
                 compenstating_offset=0 # This is used when I have no idea how the indexing works
                 ):
        self.pointer_type = pointer_type
        self.offset_from = offset_from
        self.compensating_offset = compenstating_offset
        super().__init__(position, parent, endian, comment)


    def write(self):
        raise NotImplementedError()

    def read(self):
        offset = super().read()
        value = self.pointer_type(0, self.get_rom())
        value.position = self.offset_from + (offset+self.compensating_offset) * value.get_size()
        return "OffsetPointer (val: {} ) -> {}".format(offset, value.read())


