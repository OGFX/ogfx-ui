#include <jack/jack.h>
#include <jack/ringbuffer.h>
#include <jack/midiport.h>

#include <boost/program_options.hpp>
#include <string>
#include <assert.h>
#include <iostream>
#include <cstdlib>
#include <unistd.h>

/*
  A small program to list available jack ports in 
  an easy readable JSON format
*/
int main(int argc, char *argv[]) {
  std::string name;

  bool input;
  bool output;
  bool midi;
  bool audio;
  
  namespace po = boost::program_options;
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h",
     "get some help")
    ("name,n",
     po::value<std::string>(&name)->default_value("jack_list_ports"),
     "the jack client name")
    ("input,i",
     po::value<bool>(&input)->default_value(false),
     "list input ports")
    ("output,o",
     po::value<bool>(&output)->default_value(false),
     "list output ports")
    ("input,m",
     po::value<bool>(&midi)->default_value(false),
     "list MIDI ports")
    ("audio,a",
     po::value<bool>(&audio)->default_value(false),
     "list input ports")
     ;

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return EXIT_SUCCESS;
  }

  jack_status_t jack_status;
  jack_client_t *jack_client = jack_client_open(name.c_str(), JackNullOption, &jack_status);

  if (NULL == jack_client) {
    std::cerr << "Failed to create jack client. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  const char **ports = jack_get_ports(jack_client, NULL, NULL, 0);

  std::cout << "[ ";
  for (int index = 0; ports && ports[index]; ++index) {
    jack_port_t *port = jack_port_by_name(jack_client, ports[index]);
    int flags = jack_port_flags(port);

    if (index != 0) {
      std::cout << ", ";
    }
    
    std::cout <<
      "{ " <<
      " \"name\": \"" << ports[index] << "\"," << 
      ", \"type\": \"" << jack_port_type(port) << "\"," << 
      " \"input\": " << ((flags & JackPortIsInput) != 0) << "," <<
      " \"output\": " << ((flags & JackPortIsOutput) != 0) << "," <<
      " }";
  }
  std::cout << " ]" << std::endl;
  
  jack_client_close(jack_client);
}
