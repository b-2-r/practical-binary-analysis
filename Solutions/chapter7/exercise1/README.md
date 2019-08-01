# Changing the Date Format

Create a copy of the /bin/date program and use hexedit to change the default
date format string. You may want to use strings to look for the default
format string.

## Solution

date-patcher.py

## Sample Session

```
$ python3 date-patcher.py
[*] Applying format string patch at offset 0xa944
[*] Applying nl_langinfo item patch at offset 0x2223
[*] Done applying patches
$ date
Thu Aug  1 15:48:25 CEST 2019
$ ./date-modified 
15:48:44
```
