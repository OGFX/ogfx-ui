#include <jack/jack.h>
#include <boost/program_options.hpp>
#include <string>
#include <cstdlib>
#include <iostream>
#include <vector>
#include <assert.h>

struct cc {
  int m_channel;
  int m_controller;
};

struct cc_mapping {
  /* The MIDI CC to respond to */
  cc m_cc;

  /* The lv2 port symbol of the parameter to change */
  unsigned m_port_symbol;

  /* Parameter value corresponging to cc-value 0 */
  float m_minimum;

  /* Parameter value corresponging to cc-value 127 */  
  float m_maximum;
};

int main(int argc, char *argv[]) {
  namespace po = boost::program_options;

  std::string plugin_uri;
  std::string jack_name;
  std::string jalv;
  
  cc bypass_cc;

  std::vector<std::string> mapping_strings;
  
  po::options_description desc("Allowed options");
  desc.add_options()
    ("help,h", "produce help message")
    ("uri,u", po::value<std::string>(&plugin_uri), "the URI of the plugin")
    ("name,n", po::value<std::string>(&jack_name), "the name of the jack client")
    ("jalv,j", po::value<std::string>(&jalv)->default_value("jalv"),
     "the name of the jalv executable")
    ("bypass_channel",
     po::value<int>(&bypass_cc.m_channel)->default_value(0),
     "the MIDI channel used for bypass toggle events")
    ("bypass_controller",
     po::value<int>(&bypass_cc.m_controller)->default_value(0),
     "the MIDI controller used for bypass toggle events (0: bypass, everything else: no bypass")
    ("mapping",
     po::value<std::vector<std::string>>(&mapping_strings),
     "a parameter mapping in the form of a string \"<symbol>:<channel>:<controller>:<minimum>:<maximum>\", where <symbol> is an lv2-port-symbol, <channel> and <controller> are integers between 0 and 127, <minimum> and <maximum> are floating point numbers.");

  po::variables_map vm;
  po::store(po::parse_command_line(argc, argv, desc), vm);
  po::notify(vm);

  if (vm.count("help")) {
    std::cout << desc << std::endl;
    return EXIT_SUCCESS;
  }

  assert(vm.count("uri"));
  assert(vm.count("name"));
  
  assert(bypass_cc.m_channel >= 0);
  assert(bypass_cc.m_controller >= 0);
}
