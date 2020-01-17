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

/*
  A small program that switches the stereo input signal to either
  of two output channel pairs. Which output pair to switch to 
  depends on the input to the process' stdin: a "0" routes the 
  signal to outputs 00 and 01 and a "1" routes the signal to 
  outputs 10 and 11.
*/
int main(int argc, char *argv[]) {
  std::string name;
  cc switch_cc;
  
  namespace po = boost::program_options;
  po::options_description desc("Allowed options");
  desc.add_options()
    ("name,n",
     po::value<std::string>(&name)->default_value("jack_switch"),
     "the jack client name");

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

  while (std::cin) {
    int n;
    cin >> n;
    std::cout << "got : " << n << std::endl;
  }
  
  jack_client_close(jack_client);
}
