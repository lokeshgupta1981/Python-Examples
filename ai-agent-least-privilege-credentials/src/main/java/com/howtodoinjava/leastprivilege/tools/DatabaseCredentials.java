package com.howtodoinjava.leastprivilege.tools;

import com.howtodoinjava.leastprivilege.db.DbCredential;

/** Where the findOrders tool gets its database login from. */
public interface DatabaseCredentials {
    DbCredential current();
}
