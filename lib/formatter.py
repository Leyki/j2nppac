import re
import textwrap

xml_escape_to = ("&amp;", "&quot;", "&apos;", "&lt;", "&gt;", "&#x0a;")
xml_escape_from = ("&", "\"", "'", "<", ">", "\n")

def escape_xml(text: str):
    for i in range(6):
        text = text.replace(xml_escape_from[i], xml_escape_to[i])
    return text

def wrap_text(text: str, lim: int):
    result = ""
    for line in text.split("\n"):
        if line == "": result += ""
        carried_len = 0 
        captured_words = []
        for word in line.split(" "):
            le = len(word)
            if carried_len + le + 1 <= lim:
                captured_words.append(word)
                carried_len += le + 1 
            else:
                if le > 12:
                    remanent = lim - carried_len
                    captured_words.append(word[0: remanent])
                    result += "\n" + " ".join(captured_words)
                    captured_words = [word[remanent: ]] 
                    carried_len = le - remanent
                else:
                    result += "\n" + " ".join(captured_words)
                    captured_words = [word] 
                    carried_len = le
        
        if (len(captured_words)): result += "\n" + " ".join(captured_words)
    return result

def format_annotations(line: str):
    line = line.replace("@note ", "Note - ", 1)
    line = line.replace("@patch ", "Patch - ", 1)
    line = line.replace("@bug ", "Bug - ", 1)
    line = line.replace("@event ", "Event - ", 1)
    line = line.replace("@pure", "<Pure>", 1)
    line = line.replace("@async", "<Async>", 1)
    # extra
    line = line.replace("http://www.hiveworkshop", "hiveworkshop")
    line = line.replace("https://www.hiveworkshop", "hiveworkshop")
    line = line.replace("http://", "")
    line = line.replace("https://", "")
    
    if line[0:6] == "@param": 
        line = line[7: ].replace(" ", " - ", 1)
    if line[0:2] == "* ":  
        line = "-" + line[1: ]
    return line

# i can't into regex so no escaping support
MD_INLINE_PATTERNS = (     # single lettered
    re.compile(r"\*{2}([^*\s])\*{2}"),  # strong
    re.compile(r"_{2}([^_\s])_{2}"),    # strong alt
    re.compile(r"\*([^*\s])\*"),        # em
    re.compile(r"_([^_\s])_"),          # em alt
    re.compile(r"~{2}([^~\s])~{2}"),    # del
    re.compile(r"`([^`\s])`"),          # code

    re.compile(r"\*{2}([^*\s][^*]*[^*\s])\*{2}"), # strong
    re.compile(r"\*([^*\s][^*]*[^*\s])\*"),       # em
    re.compile(r"_{2}([^_\s][^_]*[^_\s])_{2}"),   # strong alt
    re.compile(r"_([^_\s][^_]*[^_\s])_"),         # em alt
    re.compile(r"~{2}([^~\s][^~]*[^~\s])~{2}"),   # del
    re.compile(r"`([^`\s][^`]*[^`\s])`")          # code
)
md_link_pattern = re.compile(r"\[([^\[\]]*)\]\(([^\(\)]*)\)")

def remove_md(line: str):
    for pattern in MD_INLINE_PATTERNS:
        line = pattern.sub(r"\1", pattern.sub(r"\1", line))
    line = md_link_pattern.sub(r"\1 - \2", line)
    return line

unnaxeable = {"@", "-", "*", "|"}

def format_descr(func: dict, width: int, length: int, separator: int):
    result = ""
    carried_lfs = 0
    code_open = False # doesn't support unblocked code
    
    for i, line in enumerate(func["descr"]):
        if line.startswith("```"): code_open = not code_open ; continue
        if code_open: result += line
        
        line = line.strip()
        if line == "":
            if carried_lfs == 1: result += "\n"
            if carried_lfs > 1: continue
            carried_lfs += 1
        else: 
            if carried_lfs > 1: result += "\n"
            else:
                if line[0] in unnaxeable: result += "\n"
                else: result += " "
            carried_lfs = 0
            result += format_annotations(remove_md(line))

    result = wrap_text(result, width)
    result = "\n" * separator + result.strip("\n ")
    result = escape_xml(result)
    result = textwrap.shorten(result, length, replace_whitespace=False) # todo: this doesn't shorten correctly due to escaped chars
    return result


def abbreviate(take: str, patterns: dict):
    for match, repl in zip(patterns["match"], patterns["replace"]):
        if type(match) == re.Pattern:
            matched = match.sub(repl, take)
            if matched != None: 
                take = matched
        elif take == match:
            take = repl
    return take
        
