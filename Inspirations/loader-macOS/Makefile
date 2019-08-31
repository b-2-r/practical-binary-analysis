CXX=g++
OBJ=loader_demo
CONFIG_FIX=-DPACKAGE -DPACKAGE_VERSION
INCLUDE_DIR=binutils-2.32/include
LIBRARY_DIR=binutils-2.32/lib

.PHONY: all clean

all: $(OBJ)

loader.o: inc/loader.cc
	$(CXX) -std=c++11 -c -I$(INCLUDE_DIR) $(CONFIG_FIX) inc/loader.cc

loader_demo: loader.o loader_demo.cc
	$(CXX) -std=c++11 -o loader_demo loader_demo.cc loader.o -L$(LIBRARY_DIR) -lz -lintl -liberty -liconv -lbfd

clean:
	rm -f $(OBJ) *.o
