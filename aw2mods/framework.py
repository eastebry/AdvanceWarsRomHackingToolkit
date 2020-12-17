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

class Struct(object):
    
    def __init__(self, position, parent):
        self.parent = parent
        self.position = position

    def get_offset(self):
        # type: () -> int
        if isinstance(self.parent, Struct):
            return self.position +  self.parent.get_offset()
        elif isinstance(self.parent, Rom):
            return self.position
        
        return ValueError('Parent is neither patch nor rom')

    @classmethod
    def size(cls):
        raise NotImplementedError()

    def get_rom(self):
        if isinstance(self.parent, Rom):
            return self.parent

        if isinstance(self.parent, Struct):
            return self.parent.get_rom()

        return ValueError('Parent is neither patch nor rom')

    def members(self):
        return {k: v for k, v in vars(self).items() if k != 'parent' and isinstance(v, Struct)}

    def display(self):
        last_member = max(self.members().values(), key=lambda x: x.position)
        end_offset = last_member.position + last_member.size()
        bites = self.get_rom().read(self.position, end_offset)
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
        print("Position {}, Size {}".format(hex(self.position), end_offset))
        print("-" * 39)
        print("0    2    4    6    8    a    c    e")
        print("".join(final))
        print("-" * 39)

        for k, v in self.members().items():
            print("{}: ({} -> {}) {} {}".format(k, hex(v.position), hex(v.position + v.size() - 1), v.read(), v.comment))
        print("-" * 39)



class Type(Struct):

    def __init__(self, position, parent, endian='<', comment=""):
        super().__init__(position, parent)
        self.endian = endian
        self.comment = comment

    @classmethod
    def format_string_char(cls):
        raise NotImplementedError()

    def format_string(self):
        return "{}{}".format(self.endian, self.format_string_char())
    def __str__(self):
        return str(self.read())

    def read(self):
        return int(struct.unpack(
            self.format_string(),
            self.get_rom().read(self.get_offset(), self.size())
        )[0])
    
    def write(self, value):
        value = struct.pack(self.format_string(), value)
        self.get_rom().write(self.get_offset(), value)

class UInt8(Type):
    @classmethod
    def size(cls):
        return 1
    
    @classmethod
    def format_string_char(cls):
        return "B"

class UInt16(Type):
    
    @classmethod
    def size(cls):
        return 2
    
    @classmethod
    def format_string_char(cls):
        return "H"

class Char(UInt8):

    def read(self):
        return chr(super().read())

    def write(self, value):
        super().write(ord(value))


class Pointer(Type):

    @classmethod
    def size(cls):
        return 2

    @classmethod
    def format_string_char(cls):
        return "H"

class FixedLengthString(Type):

    def __init__(self, position, parent, length, endian="<", comment=""):
        super().__init__(position, parent, endian=endian, comment=comment)
        self.length = length

    def size(self):
        return self.length

    def read(self):
        char = Char(0, self)
        result = []
        while char.read() != '\x00':
            result.append(char.read())
            char.position += 1
        return ''.join(result)

class DynamicString(Type):
    """A string is a null terminated array of chars"""

    # TODO this is not a class method. The inheritance is broken
    def size(self):
        # Find the distance to the first null byte
        char = Char(0, self)
        while char.read() != '\x00':
            char.position += 1
        return char.position + 1

    def read(self):
        char = Char(0, self)
        result = []
        while char.read() != '\x00':
            result.append(char.read())
            char.position += 1
        return ''.join(result)

class RelativePointer(Type):
    """A Relative pointer is an offset from a predefined location"""
    def __init__(self,
                 position,
                 parent,
                 pointer_type,
                 offset_from,
                 endian="<",
                 comment="",
                 ):
        self.pointer_type = pointer_type
        self.offset_from = offset_from
        super().__init__(position, parent, endian, comment)

    @classmethod
    def size(cls):
        return 2

    @classmethod
    def format_string_char(cls):
        return "H"

    def write(self):
        raise NotImplementedError()

    def read(self):
        offset = super().read()
        # TODO pointer math needs to happen here
        value = self.pointer_type(self.offset_from + offset, self.get_rom())
        return value.read()


