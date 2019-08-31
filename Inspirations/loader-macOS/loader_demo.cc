/* Demonstrate the binary loader from ../inc/loader.cc */

#include <stdio.h>
#include <stdint.h>
#include <string>

#include "inc/loader.h"

int
main(int argc, char *argv[])
{
  size_t i;
  Binary bin;
  Section *sec;
  Symbol *sym;
  std::string fname;

  if(argc < 2) {
    printf("Usage: %s <binary>\n", argv[0]);
    return 1;
  }

  fname.assign(argv[1]);
  if(load_binary(fname, &bin, Binary::BIN_TYPE_AUTO) < 0) {
    return 1;
  }

  printf("loaded binary '%s' %s/%s (%u bits) entry@0x%016jx\n", 
         bin.filename.c_str(), 
         bin.type_str.c_str(), bin.arch_str.c_str(), 
         bin.bits, bin.entry);

  for(i = 0; i < bin.sections.size(); i++) {
    sec = &bin.sections[i];
    printf("  0x%016jx %-8ju %-20s %s\n", 
           sec->vma, sec->size, sec->name.c_str(), 
           sec->type == Section::SEC_TYPE_CODE ? "CODE" : "DATA");
  }

  if(bin.symbols.size() > 0) {
    printf("scanned symbol tables\n");
    for(i = 0; i < bin.symbols.size(); i++) {
      sym = &bin.symbols[i];
      printf("  %-40s 0x%016jx %s\n", 
             sym->name.c_str(), sym->addr, 
             (sym->type & Symbol::SYM_TYPE_FUNC) ? "FUNC" : "");
    }
  }

  unload_binary(&bin);

  return 0;
}

