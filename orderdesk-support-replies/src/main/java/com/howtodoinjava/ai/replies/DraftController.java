package com.howtodoinjava.ai.replies;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/drafts")
public class DraftController {

    private static final Logger log = LoggerFactory.getLogger(DraftController.class);

    public record TicketRequest(String ticket) {
    }

    public record SendRequest(String finalText) {
    }

    public record SendResult(String draftId, int changedPercent) {
    }

    private final ReplyDrafter drafter;
    private final Map<String, DraftResult> drafts = new ConcurrentHashMap<>();

    public DraftController(ReplyDrafter drafter) {
        this.drafter = drafter;
    }

    @PostMapping
    public DraftResult create(@RequestBody TicketRequest request) {
        if (request.ticket() == null || request.ticket().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "ticket is empty");
        }
        DraftResult result = drafter.draft(request.ticket());
        drafts.put(result.draftId(), result);
        return result;
    }

    @PostMapping("/{draftId}/send")
    public SendResult send(@PathVariable String draftId, @RequestBody SendRequest request) {
        if (request.finalText() == null || request.finalText().isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "finalText is empty");
        }
        DraftResult draft = drafts.remove(draftId);
        if (draft == null) {
            throw new ResponseStatusException(HttpStatus.NOT_FOUND, "no open draft " + draftId);
        }
        String original = draft.replyText() == null ? "" : draft.replyText();
        int changed = EditDistance.changedPercent(original, request.finalText());
        log.info("SENT draft={} status={} sources={} changed={}%",
                draftId, draft.status(), draft.sources().stream()
                        .map(DraftResult.Source::articleId).toList(), changed);
        return new SendResult(draftId, changed);
    }
}
