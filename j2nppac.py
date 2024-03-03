import re
from lib.formatter import *
from lib.patches   import *
from lib.ini       import *
from lib.jass      import parse_jass

in_jass                 = ["common.j", "Blizzard.j"]
in_folder               = "in/"
out_name                = "JASS"

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

# build filtered list
to_filter = []
if filter_types: to_filter.append("types")
if filter_consts: to_filter.append("constants")
if filter_functions: to_filter.append("functions")

if to_filter != []:
    filtered = parse_ini_sections("filter.ini", to_filter)

# build abbreviatures
if use_param_abbreviatures:
    abbreviations_lines = parse_ini("abbreviatures.ini")
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


# do parsing
parsed = []
for filename in in_jass:
    parsed += parse_jass(in_folder + filename, include_param_hints, include_descriptions)


# write the thing
with open(out_name + ".xml", "w", encoding="utf8") as out:
    out.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    out.write("<NotepadPlus>\n")
    out.write(t*1+"<AutoComplete>\n")
    out.write(t*2+f'<Environment ignoreCase="{"yes" if ignore_case else "no"}" startFunc="(" stopFunc=")" paramSeparator="," />\n')
    for chunk in parsed:
        if include_types and chunk["kind"] == "type":
            if filter_types and chunk["name"] in filtered["types"]: continue
            out.write(t*2+f'<KeyWord name="{chunk["name"]}" />\n')

        elif chunk["kind"] == "constant":
            if filter_consts and chunk["name"] in filtered["constants"]: continue
            out.write(t*2+f'<KeyWord name="{chunk["name"]}" />\n')
            
        elif chunk["kind"] == "function":
            if filter_functions and chunk["name"] in filtered["functions"]: continue

            if chunk["params"] == {}:
                out.write(t*2+f'<KeyWord name="{chunk["name"]}" func="yes" />\n')
            else:
                out.write(t*2+f'<KeyWord name="{chunk["name"]}" func="yes" >\n')
                if chunk["params"]["takes"] == []: 
                    if chunk["descr"] != []:
                        out.write(t*3+f'<Overload retVal="{chunk["params"]["returns"]}" descr="{format_descr(chunk, width, length, separator)}" />\n')
                    else:
                        out.write(t*3+f'<Overload retVal="{chunk["params"]["returns"]}" />\n')
                else:
                    if chunk["descr"] != []:
                        out.write(t*3+f'<Overload retVal="{chunk["params"]["returns"]}" descr="{format_descr(chunk, width, length, separator)}" >\n')
                    else:
                        out.write(t*3+f'<Overload retVal="{chunk["params"]["returns"]}">\n')
                        
                    if use_param_abbreviatures:
                        for take in chunk["params"]["takes"]:
                            take["type"] = abbreviate(take["type"], abbrs["types"])
                            take["name"] = abbreviate(take["name"], abbrs["names"])
                
                    early_wrap = 4 # todo, make into a func or something
                    # wrap earlier than description so that it hopefully looks nicer that way
                    carried_len = len(chunk["name"]) + len(chunk["params"]["takes"]) + 3 + early_wrap 
                    for take in chunk["params"]["takes"]:
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
