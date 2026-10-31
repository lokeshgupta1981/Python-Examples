package com.howtodoinjava.peopledesk;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.util.List;

import org.springframework.core.io.ClassPathResource;

public record LabelledQuestion(String id, EmployeeProfile employee, LocalDate asOf,
                               Answer.Route expectedRoute, String expectedSection, String question) {

    public static List<LabelledQuestion> load() throws IOException {
        return load("questions.psv");
    }

    public static List<LabelledQuestion> load(String file) throws IOException {
        String text = new ClassPathResource(file).getContentAsString(StandardCharsets.UTF_8);
        return text.lines().skip(1).filter(l -> !l.isBlank()).map(line -> {
            String[] f = line.split("\\|", -1);
            return new LabelledQuestion(f[0], new EmployeeProfile(f[1], f[2]), LocalDate.parse(f[3]),
                    Answer.Route.valueOf(f[4]), f[5], f[6]);
        }).toList();
    }
}
