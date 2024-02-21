# j2nppac

Parses JASS natives, functions, constants and types into a npp autocomplete format file along with descriptions and quasi-Markdown syntax support.

## Usage

Run j2nppac.py, main configurations can be made inside the script.
Jass script files you can find in [Jassdoc](https://github.com/lep/jassdoc) and [Wc3 jass history scripts](https://github.com/Luashine/wc3-jass-history-scripts>). `common.j` must always be parsed first to gather types.

**Jassdoc** should get you the latest scripts used by retail while **Wc3 JASS history scripts** should get you any version you could ever need.
Or you may also just extract the scripts from the game files yourself and feed it your own made data as well.
If you're using jassdoc's files the ability to parse up to a version of the game should be available but versioning declaration remains to be automatized.

If you want to write your own documentation for functions see: [Jassdoc#Annotations](https://github.com/lep/jassdoc?tab=readme-ov-file#how-to-write-annotations).

For j2nppac's purposes, any `@annotation` is equivalent to `annotation -` in the same line and a directive to not append the annotation line into a previous line; `@pure` and `@async` get converted to `<pure>` and `<async>` though.


## Issues/todo

* Escaping for descriptions isn't supported.
* Code not marked as such inside a code block isn't detected
* Text wrapping could be better.
