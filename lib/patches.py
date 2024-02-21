import copy

def replace_from_list(For: list, From: list, To: list):
    for i, val in enumerate(For):
        for I, Val in enumerate(From):
            if val == Val: For[i] = To[I]


def find_patches(in_folder: str, file_names: list):
    patches = []
    for file_name in file_names:
        with open(in_folder + file_name, "r", encoding="utf8") as jass:
            for line in jass:
                line = line.strip()

                if line.startswith("@patch"):
                    patch = line[7: ]
                    if patch not in patches:
                        patches.append(patch)    
    return patches


def is_ver_lower(patch: list, ordered: list):
    lp = len(patch) ; lo = len(ordered)
    le = min(lp, lo)

    for ver in range(le):
        if   int(patch[ver]) < int(ordered[ver]): return True
        elif int(patch[ver]) > int(ordered[ver]): return False
    # everything so far matches
    return False if lp > lo else True

def find_patch_place(patch: str, ordered: list):
    vers = patch.split(".")
    for oi, ov in enumerate(ordered):
        if is_ver_lower(vers, ov.split(".")):
            return oi
    return -1

raw_names  = ("1.24a", "1.24b", "1.27a", "1.27b")
norm_names = ("1.24.1", "1.24.2", "1.27.1", "1.27.2")

def reorder_patches(patches: list):
    unordered = copy.deepcopy(patches)
    replace_from_list(unordered, raw_names, norm_names) # normalize versioning

    ordered = []
    for patch in unordered:
        order = find_patch_place(patch, ordered)
        ordered.insert(order, patch) if order != -1 else ordered.append(patch)
    replace_from_list(ordered, norm_names, raw_names) # unnormalize versioning
    return ordered
