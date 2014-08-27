CXX=g++
CXXFLAGS= -O2 -pedantic -ansi
# For cross compiling to Win64.
CMG=x86_64-w64-mingw32-g++
# Must staticly link libs otherwise windows will complain about missing .dlls.
CMGFLAGS=-static -static-libgcc -static-libstdc++
CPPFILES=main.cpp utils.cpp
TARGET=los
WINTARGET=los.exe

los: $(CPPFILES)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(CPPFILES)

win: $(CPPFILES)
	$(CMG) $(CXXFLAGS) $(CMGFLAGS) -o $(WINTARGET) $(CPPFILES)

clean:
	-rm $(TARGET)
