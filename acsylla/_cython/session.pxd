cdef class Session:
    cdef:
        CassCluster* cass_cluster
        CassSession* cass_session
        object loop
        int next_key
