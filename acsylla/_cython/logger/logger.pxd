cdef class Logger:
    cdef:
        object logging_callback
        object log
        object _read_socket
        object _write_socket
        PosixToPython* posix_to_python

cdef log_level_from_str(object level)