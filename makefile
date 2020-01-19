.PHONY: clean all

all: lv2lsjson jack_switch

lv2lsjson: lv2lsjson.cc
	$(CXX) -O3 -march=native -Wall -Werror -Wno-conversion -o lv2lsjson lv2lsjson.cc `pkg-config lilv-0 --cflags --libs`

jack_switch: jack_switch.cc
	$(CXX) -O3 -march=native -Wall -Werror -Wno-conversion -o jack_switch jack_switch.cc `pkg-config jack --cflags --libs` -lboost_program_options
