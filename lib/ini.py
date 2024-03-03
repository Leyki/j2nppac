
# ini not ini
def parse_ini_sections(file: str, sections: list[str]):
    with open(file, "r", encoding="utf8") as ini:
        parsing = -1
        result = {}
        for section in sections:
            result[section] = []

        for line in ini:
            line = line.strip()
            if line == "" or line[0] == "#" or line[0] == ";": continue

            if line[0] == "[":
                for i, section in enumerate(sections): 
                    if line == "[" + section + "]":
                        parsing = i ; break
                continue
            if parsing == -1: continue

            result[sections[parsing]].append(line)
    return result

def _parse_ini(result: dict, file: str):
    with open(file, "r", encoding="utf8") as ini:
        parsing = -1

        for line in ini:
            line = line.strip()
            if line == "" or line[0] == "#" or line[0] == ";": continue

            if line[0] == "[": parsing = line[1:-1] ; continue
            if parsing == -1: continue

            if parsing not in result:
                result[parsing] = []

            result[parsing].append(line)

def parse_ini(file: str):
    result = {}
    _parse_ini(result, file)
    return result

def parse_ini_files(files: list):
    result = {}
    for file in files:
        _parse_ini(result, file)
    return result
