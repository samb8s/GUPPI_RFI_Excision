libHampel.so: libHampel.o
	gcc -shared -lgomp -o libHampel.so libHampel.o

libHampel.o: hampel_filter.c Makefile
	gcc -O3 -lm -fopenmp -DHAVE_OPENMP -fPIC -c -o libHampel.o hampel_filter.c

all:
	make libHampel.so

clean:
	rm -f *.o *.so
