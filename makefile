.PHONY: clean all

all: lv2lsjson

lv2lsjson: lv2lsjson.cc
	$(CXX) -Wall -Werror -Wno-conversion -o lv2lsjson lv2lsjson.cc `pkg-config lilv-0 --cflags --libs`
