## patchman [Page 155]

A bare-metal binary modification tool.

patchman allows to apply a single patch via commandline or 1-n patches via defining them
in a JSON encoded file.

There are two types of patches, offset or replace patches. An offset patch replaces a
byte sequence located at a given offset. A replace patch takes an original byte sequence
which gets replaced by a fake byte sequence (the actual patch).

### Patch File Format

Note that both types of patches can be mixed.

**Replace Patch**

***replace-patches.json***

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

**Offset Patch**

***offset-patches.json***

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

### Sample Session

```
```