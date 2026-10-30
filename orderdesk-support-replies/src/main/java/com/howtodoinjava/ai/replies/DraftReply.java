package com.howtodoinjava.ai.replies;

import java.util.List;

import io.swagger.v3.oas.annotations.media.ArraySchema;

public record DraftReply(String replyText,
                         @ArraySchema(maxItems = 3) List<String> citedArticleIds,
                         boolean covered) {
}
