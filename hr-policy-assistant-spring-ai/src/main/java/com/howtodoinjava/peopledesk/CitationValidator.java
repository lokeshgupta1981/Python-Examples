package com.howtodoinjava.peopledesk;

import java.util.LinkedHashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public final class CitationValidator {

    private static final Pattern LABEL = Pattern.compile("\\[([^\\[\\]]+ v\\d+, \\d+\\.\\d+)\\]");

    private CitationValidator() {
    }

    public static Set<String> citedLabels(String answer) {
        Set<String> labels = new LinkedHashSet<>();
        Matcher m = LABEL.matcher(answer);
        while (m.find()) {
            labels.add(m.group(1));
        }
        return labels;
    }

    /** An answer is valid only if it cites at least one section and every cited section was retrieved. */
    public static boolean isValid(Set<String> cited, Set<String> retrieved) {
        return !cited.isEmpty() && retrieved.containsAll(cited);
    }
}
