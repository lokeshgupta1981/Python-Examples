package com.howtodoinjava.ai.replies;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("orderdesk.replies")
public record ReplyProperties(String helpCenter, String articleBaseUrl, String indexFile,
                              double similarityThreshold, int topK) {
}
