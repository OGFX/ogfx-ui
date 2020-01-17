#include <jack/jack.h>
#include <boost/program_options.hpp>
#include <string>
#include <assert.h>
#include <iostream>
#include <cstdlib>

struct cc {
  int m_channel;
  int m_controller;
};

int channel_switch;

jack_port_t *in0;
jack_port_t *in1;

jack_port_t *out00;
jack_port_t *out01;
jack_port_t *out10;
jack_port_t *out11;

/*
  A small program that switches the stereo input signal to either
  of two output channel pairs. Which output pair to switch to 
  depends on the input to the process' stdin: a "0" routes the 
  signal to outputs 00 and 01 and a "1" routes the signal to 
  outputs 10 and 11.
*/
int main(int argc, char *argv[]) {
  std::string name;
  
  namespace po = boost::program_options;
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h",
     "get some help")
    ("name,n",
     po::value<std::string>(&name)->default_value("jack_switch"),
     "the jack client name");

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

  in0 = jack_port_register(jack_client, "in0", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
  in1 = jack_port_register(jack_client, "in1", JACK_DEFAULT_AUDIO_TYPE, JackPortIsInput, 0);
  
  out00 = jack_port_register(jack_client, "out00", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
  out01 = jack_port_register(jack_client, "out01", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
  
  out10 = jack_port_register(jack_client, "out10", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
  out11 = jack_port_register(jack_client, "out11", JACK_DEFAULT_AUDIO_TYPE, JackPortIsOutput, 0);
  
  int n;
  while (std::cin >> n) {
    // std::cout << "got : " << n << std::endl;
    if (0 == n) {
      channel_switch = 0;
    }
    if (0 != n) {
      channel_switch = 1;
    }
  }
  
  jack_client_close(jack_client);
}
