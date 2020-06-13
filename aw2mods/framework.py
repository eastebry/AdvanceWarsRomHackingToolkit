import struct

class Rom(object):
    def __init__(self, rom_file):
        # type: (str) -> None
        with open(rom_file, 'rb') as f:
            self.bites = list(f.read())
    
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

class Patch(object):
    
    def __init__(self, position, parent):
        self.parent = parent
        self.position = position

    def get_offset(self):
        # type: () -> int
        if isinstance(self.parent, Patch):
            return self.position +  self.parent.get_offset()
        elif isinstance(self.parent, Rom):
            return self.position
        
        return ValueError('Parent is neither patch nor rom')

    def get_rom(self):
        if isinstance(self.parent, Rom):
            return self.parent

        if isinstance(self.parent, Patch):
            return self.parent.get_rom()

        return ValueError('Parent is neither patch nor rom')
    

class Type(Patch):

    def __init__(self, position, parent, endian='<'):
        super().__init__(position, parent)
        self.endian = endian
    
    @classmethod
    def size(cls):
        raise NotImplementedError()

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
    
class Uint16(Type):
    
    @classmethod
    def size(cls):
        return 2
    
    @classmethod
    def format_string_char(cls):
        return "H"
    