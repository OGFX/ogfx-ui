prefix ?= /usr/local

.PHONY: clean all install

all: lv2lsjson jack_switch jack_midi_json_dump jack_list_ports

install: all
	mkdir -p ${prefix}/bin
	install lv2lsjson ${prefix}/bin/
	install jack_switch ${prefix}/bin/
	install jack_midi_json_dump ${prefix}/bin/
	install jack_list_ports ${prefix}/bin/

clean: 
	rm -f lv2lsjson jack_swith jack_midi_json_dump jack_list_ports

lv2lsjson: lv2lsjson.cc
	$(CXX) -O3 -march=native -Wall -Werror -Wno-conversion -o lv2lsjson lv2lsjson.cc `pkg-config lilv-0 --cflags --libs`

jack_switch: jack_switch.cc
	$(CXX) -O3 -march=native -Wall -Werror -Wno-conversion -o jack_switch jack_switch.cc `pkg-config jack --cflags --libs` -lboost_program_options

jack_midi_json_dump: jack_midi_json_dump.cc
	$(CXX) -g -O3 -march=native -Wall -Werror -Wno-conversion -o jack_midi_json_dump jack_midi_json_dump.cc `pkg-config jack --cflags --libs` -lboost_program_options

jack_list_ports: jack_list_ports.cc
	$(CXX) -O3 -march=native -Wall -Werror -Wno-conversion -o jack_list_ports jack_list_ports.cc `pkg-config jack --cflags --libs` -lboost_program_options
