package com.howtodoinjava.ai.replies;

final class EditDistance {

    private EditDistance() {
    }

    /** Edit distance divided by the length of the longer text, as a whole percentage. */
    static int changedPercent(String draft, String sent) {
        int longer = Math.max(draft.length(), sent.length());
        if (longer == 0) {
            return 0;
        }
        return (int) Math.round(100.0 * levenshtein(draft, sent) / longer);
    }

    /** Standard Levenshtein distance: inserts, deletes and replacements of single characters. */
    static int levenshtein(String a, String b) {
        int[] previous = new int[b.length() + 1];
        int[] current = new int[b.length() + 1];
        for (int j = 0; j <= b.length(); j++) {
            previous[j] = j;
        }
        for (int i = 1; i <= a.length(); i++) {
            current[0] = i;
            for (int j = 1; j <= b.length(); j++) {
                int cost = a.charAt(i - 1) == b.charAt(j - 1) ? 0 : 1;
                current[j] = Math.min(Math.min(current[j - 1] + 1, previous[j] + 1),
                        previous[j - 1] + cost);
            }
            int[] swap = previous;
            previous = current;
            current = swap;
        }
        return previous[b.length()];
    }
}
