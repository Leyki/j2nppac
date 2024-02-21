import re
from lib.formatter import *
from lib.patches   import *
from lib.ini   import *

in_jass                 = ["common.j", "Blizzard.j"]
in_folder               = "in/"
out_name                = "JASS"
append_version_number   = False


include_types           = False

include_param_hints     = True # autocomplete stops working while a function body is present so you might want to opt out of this
use_param_abbreviatures = False # if parameters feel a lil too large, see abbreviatures.ini
function_box_width      = 80   # maximum line length in chars, used to wrap lines
function_box_length     = 600  # if a description exceeds this many chars it will be cut off early


include_descriptions    = True # requires param_hints to be on
description_separator   = 1    # how many new lines to prefix to a description

filter_types            = True # see filter.ini
filter_consts           = True
filter_functions        = True

ignore_case             = True   # when typing if case should be ignored or not
t                       = "    " # xml file tab size


types = ["integer", "real", "boolean", "string", "handle", "code"] # primitives
functions = [] 
consts = []

filtered_types = []

abbrs = {
    "types": {
        "match": [],
        "replace": [] 
    },
    "names": {
        "match": [],
        "replace": [] 
    }
}


if not include_param_hints: include_descriptions = False
width  = function_box_width
length = function_box_length
separator = description_separator

name_pattern       = re.compile(r"([a-zA-Z][a-zA-Z0-9_]*)")
name_abbr_pattern  = re.compile(r"([a-zA-Z][a-zA-Z0-9_]*)\s*([^\s#;]*)")
namer_abbr_pattern = re.compile(r"/([^\s#;]*)\s*([^#;]*)")
spaces_pattern     = re.compile(r"\s+")
ln_comment_pattern = re.compile(r".//.*")

def parse_jass(file_name: str, types: list, functions: list, consts: list, patch: int):
    nu = 0
    descr = []
    descr_open = False
    globals_open = False
    skip_next = False
    if not patch == -1:
        hashed_patches = {} # why doe
        for i, v in enumerate(patches):
            hashed_patches[v] = i

    with open(file_name, "r", encoding="utf8") as jass:
        for line in jass:
            nu += 1
            parsed_keyword = False
            line = line.strip()

            # descriptions
            if   line.startswith("/**"):descr_open = True  ; continue
            elif line.startswith("*/"): descr_open = False ; continue
            if descr_open: 
                if line == "": descr.append("") ; continue

                if not patch == -1 and line[0:6]=="@patch":
                    if hashed_patches[line[7: ]] > patch:
                        skip_next = True
                        descr = []
                if include_descriptions:
                    if not skip_next: descr.append(line)
                continue
            
            line = line.replace(",", " ")
            line = spaces_pattern.sub(" ", line)
            line = ln_comment_pattern.sub("", line)
            
     
            if line == "" or line == "//": continue
            if line == "globals":    globals_open = True;  continue
            if line == "endglobals": globals_open = False; continue
            
            i = 0
            parse = line.split(" ")

            if parse[i] == "constant": i += 1

            if parse[i] == "type":
                if not skip_next: types.append(parse[i+1])
                parsed_keyword = True

            if globals_open == True and parse[i] in types:
                if not skip_next:
                    if parse[i+1] == "array": i += 1
                    consts.append(parse[i+1])
                parsed_keyword = True

            # functions
            if parse[i] == "native" or parse[i] == "function":
                parsed_keyword = True
                if skip_next: continue

                if filter_functions and parse[i+1] in filtered["functions"]: 
                    descr = [] ; continue
                #native/function {name} takes [{type} {name}] returns {type}
                if include_param_hints:
                    func = {}
                    func["name"] = parse[i+1]
                    func["takes"] = []
                    if parse[i+3] == "nothing": i -= 1
                    else:
                        while parse[i+3] != "returns":
                            func["takes"].append({"type": parse[i+3], "name": parse[i+4]})
                            i += 2
                    func["returns"] = parse[i+4]

                    if descr != []: func["descr"] = descr
                    #print(descr)
                    functions.append(func)
                else: functions.append(parse[i+1])

            if parsed_keyword: descr = [] ; skip_next = False
        # print(nu, f"'{parse}'")


# build filtered list
to_filter = []
if filter_types: to_filter.append("types")
if filter_consts: to_filter.append("constants")
if filter_functions: to_filter.append("functions")

if to_filter != []:
    filtered = parse_ini("filter.ini", to_filter)

# build abbreviatures
if use_param_abbreviatures:
    abbreviations_lines = parse_ini_all("abbreviatures.ini")
    for key in abbreviations_lines.keys():
        for line in abbreviations_lines[key]:
            name  = name_abbr_pattern.match(line)
            namer = namer_abbr_pattern.match(line)
            if namer:
                abbrs[key]["match"].append(re.compile(namer.group(1)))
                abbrs[key]["replace"].append(namer.group(2))
            elif name:
                abbrs[key]["match"].append(name.group(1))
                abbrs[key]["replace"].append(name.group(2))
            else: 
                print(f'Invalid abbrevation - "{line}"')

# build patches
patches = find_patches(in_folder, in_jass)

if patches == []: patch = -1
else:
    patches = reorder_patches(patches)

#interface
    print(*patches)

    patch = ""
    while(True):
        print("Found patch labels. Type a patch number to parse up to that patch or press enter for highest/everything.")
        patch = input()
        if patch == "": patch = -1
        else:
            for i, v in enumerate(patches):
                if patch == v: patch = i
        if type(patch) == int: break
    if patch == len(patches)-1: patch = -1
    if append_version_number: out_name += patches[patch]

# do parsing
for filename in in_jass:
    parse_jass(in_folder + filename, types, functions, consts, patch)

with open(out_name + ".xml", "w", encoding="utf8") as out:
    out.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    out.write("<NotepadPlus>\n")
    out.write(t*1+"<AutoComplete>\n")
    out.write(t*2+f'<Environment ignoreCase="{"yes" if ignore_case else "no"}" startFunc="(" stopFunc=")" paramSeparator="," />\n')

    if include_types:
        for Type in types:
            if not filter_types or Type not in filtered["types"]:
                out.write(t*2+f'<KeyWord name="{Type}" />\n')

    for const in consts:
        if filter_consts and const in filtered["constants"]: continue
        out.write(t*2+f'<KeyWord name="{const}" />\n')
        
    for func in functions:
        if type(func) == str: 
            out.write(t*2+f'<KeyWord name="{func}" func="yes" />\n') ; continue
        out.write(t*2+f'<KeyWord name="{func["name"]}" func="yes" >\n')

        if func["takes"] == []: 
            if "descr" in func:
                out.write(t*3+f'<Overload retVal="{func["returns"]}" descr="{format_descr(func, width, length, separator)}" />\n')
            else:
                out.write(t*3+f'<Overload retVal="{func["returns"]}" />\n')
        else:
            if "descr" in func:
                out.write(t*3+f'<Overload retVal="{func["returns"]}" descr="{format_descr(func, width, length, separator)}" >\n')
            else:
                out.write(t*3+f'<Overload retVal="{func["returns"]}">\n')
                
            if use_param_abbreviatures:
                for take in func["takes"]:
                    take["type"] = abbreviate(take["type"], abbrs["types"])
                    take["name"] = abbreviate(take["name"], abbrs["names"])
            
            early_wrap = 4 # todo, make into a func or something
            # wrap earlier than description so that it hopefully looks nicer that way
            carried_len = len(func["name"]) + len(func["takes"]) + 3 + early_wrap 
            for take in func["takes"]:
                carried_len += 3 + len(take["type"]) + len(take["name"])
                if carried_len >= width:
                    
                    if len(take["name"]) > 8:
                        remanent = width - carried_len
                        take["name"] =  take["name"][0:remanent] + "&#x0a;" + take["name"][remanent: ]
                        carried_len = len(take["name"]) - remanent + early_wrap
                    else:
                        carried_len = early_wrap
                        take["name"] = take["name"] + "&#x0a;"

                out.write(t*4+f'<Param name="{take["type"]} {take["name"]}"/>\n')
            out.write(t*3+f'</Overload>\n')
        out.write(t*2+f'</KeyWord>\n')
        
    out.write(t*1+"</AutoComplete>\n")
    out.write("</NotepadPlus>\n")

print("Done!")
