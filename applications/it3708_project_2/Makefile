CXX=clang++
CXXFLAGS=-std=c++0x -O3 -Wall

EMCC=emcc
EMCCFLAGS=-O2 

LD=ld
LDFLAGS=

TARGET=test_neurons
SANDBOX_TARGET=sandbox/izhikevich.js


all: $(TARGET) $(SANDBOX_TARGET)


$(SANDBOX_TARGET): js_bindings.cc izhikevich.cc
	$(EMCC) $(EMCCFLAGS) $^ -s EXPORTED_FUNCTIONS="['_izhikevichTest']"\
			-o $@


$(TARGET): test_neurons.cc izhikevich.cc
	$(CXX) $(CXXFLAGS) $^ -o $@


.PHONY: clean
clean: 
	rm -fr $(TARGET) $(SANDBOX_TARGET) *.o *.pyc __pycache__
