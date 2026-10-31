package com.howtodoinjava.peopledesk;

import java.time.LocalDate;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class AskController {

    public record AskRequest(String question, LocalDate asOf) {
    }

    private final PolicyAssistant assistant;

    public AskController(PolicyAssistant assistant) {
        this.assistant = assistant;
    }

    // in production, region and employee type come from the login token, not from headers
    @PostMapping("/api/ask")
    public Answer ask(@RequestHeader("X-Region") String region,
                      @RequestHeader("X-Employee-Type") String employeeType,
                      @RequestBody AskRequest request) {
        LocalDate asOf = request.asOf() != null ? request.asOf() : LocalDate.now();
        return assistant.ask(request.question(), new EmployeeProfile(region, employeeType), asOf);
    }
}
