# patchman [Page 155]

A bare-metal binary modification tool.

***patchman*** allows to apply a single patch via command line, or 1-n patches via defining them in a JSON encoded file.

There are two types of patches, offset and replace patches. An offset patch replaces a byte sequence located at a given offset. A replace patch takes an original byte sequence which gets replaced by a fake byte sequence (the actual patch).

**Note**:

All hex values (offsets and bytes) must not contain the ***0x*** prefix!

## Patch File Format

Note that both types of patches can be mixed.

### Replace Patch

File ***replace-patches.json***:

```
{
    "patches": [
        {
            "orig_bytes":    "e822f4ffff",
            "patched_bytes": "e882df3f00"
        },
        {
            "orig_bytes":    "e8c2f3ffff",
            "patched_bytes": "e8b1e33f00"
        }
    ]
}
```

###  Offset Patch

File ***offset-patches.json***:

```
{
    "patches": [
        {
            "offset":    "2cf9",
            "patched_bytes": "e882df3f00"
        },
        {
            "offset":    "2909",
            "patched_bytes": "e8b1e33f00"
        }
    ]
}
```

## Sample Session

Show program's help message and exit: 

```
$ ./patchman.py -h
usage: patchman.py [-h] [-v] (-r ORIG PATCH | -o OFFS PATCH | -f PATH) binary

A bare-metal binary modification tool

positional arguments:
  binary         binary to patch

optional arguments:
  -h             show this help message and exit
  -v             show program's version number and exit

patching arguments:
  one of the arguments -r -o -f is required

  -r ORIG PATCH  replaces ORIG bytes with PATCH bytes
  -o OFFS PATCH  replaces the bytes starting at offset OFFS with PATCH bytes
  -f PATH        reads the patch definitions from the JSON file at path PATH
```

Patch ***binary*** by replacing the original byte sequence ***e822f4ffff*** with ***e882df3f00***:

```
$ ./patchman.py -r e822f4ffff e882df3f00 binary
[patchman::dbg] Applying patch 0xe882df3f00 at offset 0x2cf9
```

Patch ***binary*** by replacing the byte sequence starting at offset ***2909*** with ***e8b1e33f00***:

```
$ ./patchman.py -o 2909 e8b1e33f00 binary
[patchman::dbg] Applying patch 0xe8b1e33f00 at offset 0x2909
```

Patch ***binary*** by applying the (replace) patches defined in ***replace-patches.json***:

```
$ ./patchman.py -f replace-patches.json binary
[patchman::dbg] Applying patch 0xe882df3f00 at offset 0x2cf9
[patchman::dbg] Applying patch 0xe8b1e33f00 at offset 0x2909
```

Patch ***binary*** by applying the (offset) patches defined in ***offset-patches.json***:

```
$ ./patchman.py -f offset-patches.json binary
[patchman::dbg] Applying patch 0xe882df3f00 at offset 0x2cf9
[patchman::dbg] Applying patch 0xe8b1e33f00 at offset 0x2909
```