#include <jack/jack.h>
#include <jack/ringbuffer.h>
#include <jack/midiport.h>

#include <boost/program_options.hpp>
#include <string>
#include <assert.h>
#include <iostream>
#include <cstdlib>
#include <unistd.h>

jack_port_t *in0;

jack_ringbuffer_t *ringbuffer;

const size_t message_size = 3;

extern "C" {
  int process(jack_nframes_t nframes, void *arg) {
    // void *in0_buffer = jack_port_get_buffer(in0, nframes);

    jack_nframes_t number_of_events = jack_midi_get_event_count(in0);

    for (jack_nframes_t event_index = 0; event_index < number_of_events; ++event_index) {
      jack_midi_event_t event;

      jack_midi_event_get(&event, in0, event_index);

      if (3 != event.size) {
	continue;
      }

      // CC
      if ((event.buffer[0] & (128 + 32 + 16)) == (128 + 32 + 16)) {
	jack_ringbuffer_write(ringbuffer, (const char*)event.buffer, 3);
      }

      // Pitch bend
      if ((event.buffer[0] & (128 + 64 + 32)) == (128 + 64 + 32)) {
	jack_ringbuffer_write(ringbuffer, (const char*)event.buffer, 3);
      }
    }
    
    return 0;
  }
}

/*
  A small program that dumps the midi event stream it
  gets to stdout as JSON objects (one per line) in the form:

  { bytes: [ 76, 23, 11 ] }

  where bytes are values between 0 and 255. Right now this 
  program is limited to the 3-byte messages control change
  and pitch bend change.
*/
int main(int argc, char *argv[]) {
  std::string name;
  
  namespace po = boost::program_options;
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h",
     "get some help")
    ("name,n",
     po::value<std::string>(&name)->default_value("jack_midi_json_dump"),
     "the jack client name");

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return EXIT_SUCCESS;
  }

  ringbuffer = jack_ringbuffer_create(2 << 16);
  
  jack_status_t jack_status;
  jack_client_t *jack_client = jack_client_open(name.c_str(), JackNullOption, &jack_status);

  if (NULL == jack_client) {
    std::cerr << "Failed to create jack client. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  in0 = jack_port_register(jack_client, "in0", JACK_DEFAULT_MIDI_TYPE, JackPortIsInput, 0);

  if (0 != jack_set_process_callback(jack_client, process, 0)) {
    std::cerr << "Failed to set process callback. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  if (0 != jack_activate(jack_client)) {
    std::cerr << "Failed to activate. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }


  while(true) {
    usleep(1000);

    size_t available;

    while((available = jack_ringbuffer_read_space(ringbuffer)) >= 3) {
      char data[3];
      jack_ringbuffer_read(ringbuffer, data, 3);

      std::cout
	<< "{ \"bytes\": [ "
	<< data[0] << ", " << data[1] << ", " << data[2]
	<< " ] }"
	<< std::endl;
    }
  }
  
  jack_client_close(jack_client);
}
