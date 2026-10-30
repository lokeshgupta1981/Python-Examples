package com.howtodoinjava.ai.replies;

import java.util.List;

public record DraftResult(String draftId, Status status, String reason,
                          String replyText, List<Source> sources, List<Source> retrieved) {

    public enum Status { DRAFT, NO_DRAFT }

    public record Source(String articleId, String title, String url, double score) {
    }

    public static DraftResult noDraft(String draftId, String reason, List<Source> retrieved) {
        return new DraftResult(draftId, Status.NO_DRAFT, reason, null, List.of(), retrieved);
    }
}
