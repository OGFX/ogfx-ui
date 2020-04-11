#include <lilv/lilv.h>
#include <cstdlib>
#include <iostream>
#include <sstream>
#include <stdexcept>

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
    std::stringstream str;
    try {
      str << "  {\n";
      const LilvPlugin *plugin = lilv_plugins_get(plugins, iter);
      if (NULL == plugin) {
        throw std::runtime_error("failed to get plugin");
      }
    
      const LilvNode *uri_node = lilv_plugin_get_uri(plugin);
      if (NULL == uri_node) {
        throw std::runtime_error("failed to get uri");
      }
      
      str << "    \"uri\": \"" << lilv_node_as_uri(uri_node) << "\",\n";

      const LilvNode *name_node = lilv_plugin_get_name(plugin);
      if (NULL == name_node) {
        throw std::runtime_error("failed to get name");
      }
      str << "    \"name\": \"" << lilv_node_as_string(name_node) << "\",\n";
    
      str << "    \"ports\": [\n";
      for (uint32_t port_index = 0; port_index < lilv_plugin_get_num_ports(plugin); ++port_index) {
        const LilvPort *port = lilv_plugin_get_port_by_index(plugin, port_index);

        if (0 == port_index) {
          str << "        ";
        } else {
          str << "      , ";
        }
        str << "{\n";

        const LilvNode *port_symbol_node = lilv_port_get_symbol(plugin, port);
        if (NULL == port_symbol_node) {
          throw std::runtime_error("failed to get port symbol");
        }
        str << "          \"symbol\": \"" << lilv_node_as_string(port_symbol_node) << "\",\n";

        const LilvNode *port_name_node = lilv_port_get_name(plugin, port);
        if (NULL == port_name_node) {
          throw std::runtime_error("failed to get port name");
        }
        str << "          \"name\": \"" << lilv_node_as_string(port_name_node) << "\",\n";

        str << "          \"http://lv2plug.in/ns/lv2core#InputPort\":";
        if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#InputPort"))) {
          str << " true";
        } else {
          str << " false";
        }
        str << ",\n";
      
        str << "          \"http://lv2plug.in/ns/lv2core#OutputPort\":";
        if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#OutputPort"))) {
          str << " true";
        } else {
          str << " false";
        }
        str << ",\n";
      
        str << "          \"http://lv2plug.in/ns/lv2core#AudioPort\":";
        if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#AudioPort"))) {
          str << " true";
        } else {
          str << " false";
        }
        str << ",\n";
      
        str << "          \"http://lv2plug.in/ns/lv2core#ControlPort\":";
        if (lilv_port_is_a(plugin, port, lilv_new_uri(world, "http://lv2plug.in/ns/lv2core#ControlPort"))) {
          str << " true";
        } else {
          str << " false";
        }
        str << ",\n";

        str << "          \"range\": ";
        LilvNode *default_value;
        LilvNode *minimum_value;
        LilvNode *maximum_value;

        lilv_port_get_range(plugin, port, &default_value, &minimum_value, &maximum_value);
        if (NULL != default_value && NULL != minimum_value && NULL != maximum_value) {
          str << "[ " << lilv_node_as_float(default_value) << ", " << lilv_node_as_float(minimum_value) << ", " << lilv_node_as_float(maximum_value) << " ]";
        } else {
          // FIXME: What about defaults if the port has no info?
          str << "[ 0, -1, 1 ]";
        }
        str << "\n";
      
        str << "        }\n";
      }
      // ports
      str << "     ]\n";
    
      str << "  }";
    
      iter = lilv_plugins_next(plugins, iter);
      
      if (iter != NULL) {
        str << ",";
      }
      str << "\n";
      std::cout << str.str();
    }
    catch(...) {
      iter = lilv_plugins_next(plugins, iter);
    }
  }

  std::cout << "]\n"; 
  return EXIT_SUCCESS;
}
