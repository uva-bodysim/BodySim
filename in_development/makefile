CXX=g++
CXXFLAGS= -O2 -pedantic -ansi
CPPFILES=main.cpp utils.cpp
TARGET=los

los: $(CPPFILES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(CPPFILES)

clean:
	-rm $(TARGET)
