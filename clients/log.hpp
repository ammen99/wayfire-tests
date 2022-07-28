#include <iostream>
#include <fstream>

namespace logger
{
struct log_state
{
    std::string name;
    std::ofstream out;
    int fd;


    static log_state& get()
    {
        static log_state ls;
        return ls;
    }
};

inline void init(int argc, char **argv)
{
    if (argc < 2)
    {
        std::cerr << "Program requires at least 2 arguments, the app-id and the log path!" << std::endl;
        std::exit(-1);
    }

    log_state::get().name = argv[1];
    log_state::get().out.open(argv[2], std::ios::ate | std::ios::trunc);
}

inline void log(std::string msg)
{
    log_state::get().out << msg << std::endl;
    log_state::get().out.flush();

    // For debugging
    std::cout << msg << std::endl;
}
}
