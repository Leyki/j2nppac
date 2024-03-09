import re

types = ["integer", "real", "boolean", "string", "handle", "code"] # primitives
hashed_types = { "integer", "real", "boolean", "string", "handle", "code" }

spaces_pattern     = re.compile(r"\s+")
ln_comment_pattern = re.compile(r".//.*")

const_hash    = hash("constant")
type_hash     = hash("type")
func_hash     = hash("function")
native_hash   = hash("native")

array_hash    = hash("array")
nothing_hash  = hash("nothing")
returns_hash  = hash("returns")


def parse_jass(file_name: str, keep_params=False, keep_descr=False, keep_extra=False, keep_line=False) -> list:
    """
    Parses a jass file chunks as found.
    `chunk = { "kind": "type" | "constant", "name": str, "descr": list, "line": str | None }`
                `| { "kind": "function", "name": str, "params": dict, "descr": list, "line": line | None}`
                `| { "kind": "extra", "line": str | None }.`
    """
    # nu = 0
    chunks = []

    descr  = []
    params = {}
    descr_open = False

    with open(file_name, "r", encoding="utf8") as jass:
        for line in jass:
            # nu += 1
            parse = line.strip()

            # descriptions
            if  parse.startswith("/**"):descr_open = True  ; continue
            elif parse.startswith("*/"): descr_open = False ; continue
            if descr_open:
                if keep_descr: descr.append(line)
                continue

            if not keep_line: line = None
            
            parse = parse.replace(",", " ")
            parse = spaces_pattern.sub(" ", parse)
            parse = ln_comment_pattern.sub("", parse)
            
            i = 0
            parse = parse.split(" ")
            parse_hash = hash(parse[i])
            if parse_hash == const_hash: 
                i += 1
                parse_hash = hash(parse[i])

            # types
            if parse_hash == type_hash:
                types.append(parse[i+1])
                hashed_types.add(parse[i+1])
                chunks.append({ "kind": "type", "name": parse[i+1], "descr": descr, "line": line })
                descr = []
            # globals
            elif parse[i] in hashed_types:
                if hash(parse[i+1]) == array_hash: i += 1
                chunks.append({ "kind": "constant", "name": parse[i+1], "descr": descr, "line": line })
                descr = []
            # functions
            elif parse_hash == func_hash or parse_hash == native_hash: 
                # native/function {name} takes [{type} {name}] returns {type}
                name = parse[i+1]
                if keep_params:
                    params = {}
                    params["takes"] = []
                    if hash(parse[i+3]) == nothing_hash: i -= 1
                    else:
                        while hash(parse[i+3]) != returns_hash:
                            params["takes"].append({"type": parse[i+3], "name": parse[i+4]})
                            i += 2
                    params["returns"] = parse[i+4]

                chunks.append({ "kind": "function", "name": name, "params": params, "descr": descr, "line": line })

                descr = []
            # extra
            elif keep_extra:
                chunks.append({ "kind": "extra", "line": line })
            
        # print(nu, f"'{parse}'")
    return chunks


def parse_jass_names(file_name: str) -> list:
    # nu = 0
    names = []
    with open(file_name, "r", encoding="utf8") as jass:
        for line in jass:
            # nu += 1
            line = line.strip()

            line = spaces_pattern.sub(" ", line)
            line = ln_comment_pattern.sub("", line)

            parse = line.split(" ")
            i = 0
            parse_hash = hash(parse[i])
            if parse_hash == const_hash:
                i += 1
                parse_hash = hash(parse[i])

            # types
            if parse_hash == type_hash:
                types.append(parse[i+1])
                hashed_types.add(parse[i+1])
                names.append(parse[i+1])
            # globals
            elif parse[i] in hashed_types:
                if hash(parse[i+1]) == array_hash: i += 1
                names.append(parse[i+1])
            #functions 
            elif parse_hash == native_hash or parse_hash == func_hash:
                names.append(parse[i+1])
                    # print(nu, parse[i+1])
    return names
