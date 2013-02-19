CC=gcc
CFLAGS=-std=gnu99 -lm -O3 -Wall -Wextra
TARGET=test_neurons

$(TARGET): test_neurons.c
	$(CC) $(CFLAGS) $< -o $@

.PHONY: profile
profile: test_neurons.c
	$(CC) $(CFLAGS) -pg $< -o $j.prof
	time ./$>.prof data/izzy-train1.dat 8960 waveform < \
		data/profiling_test_data > /dev/null
	gprof $>.prof gmon.out > prof.res
	rm $>.prof 

.PHONY: indent
indent: 
	echo TODO TODO

.PHONY: clean
clean: 
	rm -f $(TARGET) gmon.out prof.res

