#include <lilv/lilv.h>
#include <cstdlib>
#include <boost/program_options.hpp>
#include <iostream>

/**
   A simple little utility to dump out all LV2-plugins on the 
   system along with some of their associated data as a
   JSON-Array
*/

int main(int argc, char* argv[])
{
  LilvWorld *world = lilv_world_new();
  lilv_world_load_all(world);
  const LilvPlugins *plugins = lilv_world_get_all_plugins(world);

  std::cout << "[\n";
  
  LilvIter *iter = lilv_plugins_begin(plugins);
  while (iter != NULL) {
    std::cout << "  {\n";
    const LilvPlugin *plugin = lilv_plugins_get(plugins, iter);
    
    const LilvNode *uri_node = lilv_plugin_get_uri(plugin);
    std::cout << "    \"uri\": \"" << lilv_node_as_uri(uri_node) << "\",\n";

    const LilvNode *name_node = lilv_plugin_get_name(plugin);
    std::cout << "    \"name\": \"" << lilv_node_as_string(name_node) << "\",\n";
    
    std::cout << "    \"ports\": [\n";
    for (uint32_t port_index = 0; port_index < lilv_plugin_get_num_ports(plugin); ++port_index) {
      const LilvPort *port = lilv_plugin_get_port_by_index(plugin, port_index);

      const LilvNode *port_symbol_node = lilv_port_get_symbol(plugin, port);
      if (0 == port_index) {
        std::cout << "        ";
      } else {
        std::cout << "      , ";
      }
      std::cout << "{\n";
      std::cout << "          \"symbol\": \"" << lilv_node_as_string(port_symbol_node) << "\",\n";

      std::cout << "          \"http://lv2plug.in/ns/lv2core#InputPort\":";
      if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#InputPort"))) {
        std::cout << " true";
      } else {
        std::cout << " false";
      }
      std::cout << ",\n";
      
      std::cout << "          \"http://lv2plug.in/ns/lv2core#OutputPort\":";
      if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#OutputPort"))) {
        std::cout << " true";
      } else {
        std::cout << " false";
      }
      std::cout << ",\n";
      
      std::cout << "          \"http://lv2plug.in/ns/lv2core#AudioPort\":";
      if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#AudioPort"))) {
        std::cout << " true";
      } else {
        std::cout << " false";
      }
      std::cout << ",\n";
      
      std::cout << "          \"http://lv2plug.in/ns/lv2core#ControlPort\":";
      if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#ControlPort"))) {
        std::cout << " true";
      } else {
        std::cout << " false";
      }
      std::cout << "\n";

      LilvNode *default_value;
      LilvNode *minimum_value;
      LilvNode *maximum_value;

      lilv_port_get_range(plugin, port, &default_value, &minimum_value, &maximum_value);
      if (NULL != default_value && NULL != minimum_value && NULL != maximum_value) {

      }
      
      std::cout << "        }\n";
    }
    // ports
    std::cout << "     ]\n";
    
    std::cout << "  }";
    
    iter = lilv_plugins_next(plugins, iter);
    
    if (iter != NULL) {
      std::cout << ",";
    }
    std::cout << "\n";
    
  }

  std::cout << "]\n"; 
  return EXIT_SUCCESS;
}
