package com.howtodoinjava.leastprivilege.tools;

/** Where the cancelOrder tool gets a token for the Orders API from. */
public interface OrdersTokens {
    String tokenFor(String userAccessToken);
}
