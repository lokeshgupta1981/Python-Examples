package com.howtodoinjava.trailgear;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("trailgear.search")
public record SearchProperties(String documentPrefix, String queryPrefix,
        int dimensions, int candidates, int rrfK) {
}
