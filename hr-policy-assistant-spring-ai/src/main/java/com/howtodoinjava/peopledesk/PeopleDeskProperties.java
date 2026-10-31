package com.howtodoinjava.peopledesk;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("peopledesk")
public record PeopleDeskProperties(double similarityThreshold, int topK, String hrContact) {
}
