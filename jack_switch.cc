#include <jack/jack.h>
#include <boost/program_options.hpp>
#include <string>
#include <assert.h>
#include <iostream>
#include <cstdlib>

int channel_switch;

jack_port_t *in0;
jack_port_t *in1;

jack_port_t *out00;
jack_port_t *out01;
jack_port_t *out10;
jack_port_t *out11;

extern "C" {
  int process(jack_nframes_t nframes, void *arg) {
    void *in0_buffer = jack_port_get_buffer(in0, nframes);
    void *in1_buffer = jack_port_get_buffer(in1, nframes);
    void *out00_buffer = jack_port_get_buffer(out00, nframes);
    void *out01_buffer = jack_port_get_buffer(out01, nframes);
    void *out10_buffer = jack_port_get_buffer(out10, nframes);
    void *out11_buffer = jack_port_get_buffer(out11, nframes);
    
    if (0 == channel_switch) {
      memcpy(out00_buffer, in0_buffer, nframes * sizeof(float));
      memcpy(out01_buffer, in1_buffer, nframes * sizeof(float));

      memset(out10_buffer, 0, nframes * sizeof(float));
      memset(out11_buffer, 0, nframes * sizeof(float));
    } else {
      memset(out00_buffer, 0, nframes * sizeof(float));
      memset(out01_buffer, 0, nframes * sizeof(float));

      memcpy(out10_buffer, in0_buffer, nframes * sizeof(float));
      memcpy(out11_buffer, in1_buffer, nframes * sizeof(float));
    }
    return 0;
  }
}

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

  if (0 != jack_set_process_callback(jack_client, process, 0)) {
    std::cerr << "Failed to set process callback. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  if (0 != jack_activate(jack_client)) {
    std::cerr << "Failed to activate. Exiting..." << std::endl;
    return EXIT_FAILURE;
  }

  std::cout << "0CR for output channels 00/01, 1CR for output channels 10/11. EOF to quit" << std::endl;
  
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
