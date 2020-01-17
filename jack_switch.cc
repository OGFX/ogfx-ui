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

int main(int argc, char *argv[]) {
  std::string name;
  cc switch_cc;
  
  namespace po = boost::program_options;
  po::options_description desc("Allowed options");
  desc.add_options()
    ("name,n",
     po::value<std::string>(&name)->default_value("jack_switch"),
     "the jack client name")
    ("channel",
     po::value<int>(&switch_cc.m_channel)->default_value(0),
     "the MIDI channel (0-127)")
    ("controller",
     po::value<int>(&switch_cc.m_controller)->default_value(0),
     "the MIDI CC number (0-127)");

  assert(switch_cc.m_channel >= 0);
  assert(switch_cc.m_controller >= 0);

  jack_port_t *in0;
  jack_port_t *in1;

  jack_port_t *out00;
  jack_port_t *out01;
  jack_port_t *out10;
  jack_port_t *out11;

  jack_status_t jack_status;
  jack_client_t *jack_client = jack_client_open(name.c_str(), JackNullOption, &jack_status);

  if (NULL == jack_client) {
    std::cerr << "Failed to create jack client. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  jack_client_close(jack_client);
}
