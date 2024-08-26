class BinaryFile:

    def __init__(self, file_name):
        self.file_name = file_name
        self.content = self.read_content()
    
    #Get value of offset, return in decimal or hex
    def get(self, offset, type = "dec"):
        high_byte = self.content[offset]
        low_byte = self.content[offset+1]

        if(type=="dec"):
            return((low_byte << 8) | high_byte)
        if(type=="hex"):
            return hex((low_byte << 8) | high_byte)
    
    #Set value of offset in decimal
    def set(self, offset, value):
        high_byte = (value >> 8) & 0xFF
        low_byte = value & 0xFF
        value = bytes(value)
        self.content[offset] = low_byte
        self.content[offset + 1] = high_byte
    
    #Read file contents
    def read_content(self):
        f = open(self.file_name, 'r+b')
        content = bytearray(f.read())
        return content
    
    #Compare file to winols file, return percentage match
    def compare_winols_file(self, winols_file):
        find = 0
        found = 0
        if(len(winols_file.required)>0):
            for line in winols_file.required:
                if(line['type']=="search"):
                    for x, value in enumerate(line['values']):
                        if(value !="?"):
                            find += 1
                            value_in_file = self.get(int(line['offset'],16) + (x*2))
                            if(int(value_in_file) == int(value)):
                                found += 1

        if find !=0:
            if found !=0:
                return round(found/find*100, 2)
            else:
                return 0
        return False
        

    #Apply winols file to files content
    def apply_winols_file(self, winols_file):
        if(len(winols_file.replace)>0):
            for line in winols_file.replace:
                if(line['type']=="replace"):
                    for x, value in enumerate(line['values']):
                        if(value !="?"):
                            self.set(int(line['offset'], 16) + (x*2), int(value))
    
    
    #Save current content to new file
    def save_file(self, save_file_name):
        f = open(save_file_name, "w+b")
        f.write(self.content)
        

    

class WinOlsFile:

    def __init__(self, file_name):
        self.file_name = file_name
        self.content = self.read_content()
        self.required = self.get_required()
        self.replace = self.get_replace()

    #Read file content
    def read_content(self):
        f = open(self.file_name, 'r')
        content = f.readlines()
        return content

    #Find all required values and parse them
    def get_required(self):
        start, stop = 0, 0
        lines = []
        for x, line in enumerate(self.content):
            if(line.strip()=="begin_requires"):
                start = x + 1
            if(line.strip()=="end_requires"):
                stop = x
        for line in self.content[start:stop]:
            lines.append(self.parse_line(line))
        
        return lines
    
    #Find all values to be replaced in absolute form and parse them
    def get_replace(self):
        start, stop = 0, 0
        lines = []
        for x, line in enumerate(self.content):
            if(line.strip()=="begin_executable"):
                start = x + 1
            if(line.strip()=="end_executable"):
                stop = x

        for line in self.content[start:stop]:
            parsed_line = self.parse_line(line)
            if(parsed_line['type'] == "replace" and parsed_line['type2'] == "absolute"):
                lines.append(parsed_line)
        
        return lines
    
    
    #Parse line and return formatted content
    def parse_line(self, line):
        data = None
        split = line.strip().replace('"','').split(" ")
        if(split[0] == "search"):
            values = split[6:]
            data = {
                "type" : split[0],
                "name" : split[1],
                "bit_type" : split[2],
                "offset" : self.hex_to_hex(split[3]),
                "offset_offset" : self.hex_to_hex(split[4]),
                "allowed_percentage" : int(split[5].replace("%","")),
                "values" : values
            }
        if(split[0] == "replace"):
            values = split[6:]
            data = {
                "type" : split[0],
                "name" : split[1],
                "bit_type" : split[2],
                "offset" : self.hex_to_hex(split[3]),
                "type1" : split[4],
                "type2" : split[5],
                "values" : values
            }

        return data
    

    #Convert hex string to hex "int"
    def hex_to_hex(self, value):
        return hex(int(value,16))