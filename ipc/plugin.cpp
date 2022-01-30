#include <wayfire/singleton-plugin.hpp>
#include <getopt.h>

#include "ipc.hpp"

namespace wf
{
class ipc_plugin_t
{
  public:
    ipc_plugin_t()
    {
        char *pre_socket = getenv("_WAYFIRE_SOCKET");
        std::string socket = pre_socket ?: "/tmp/wayfire.socket";
        server = std::make_unique<ipc::server_t>(socket);
    }

    std::unique_ptr<ipc::server_t> server;
};
}

DECLARE_WAYFIRE_PLUGIN((wf::singleton_plugin_t<wf::ipc_plugin_t, false>));
