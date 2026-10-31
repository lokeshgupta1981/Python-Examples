package com.howtodoinjava.ai.eval;

/** One graded call: which setup, which run, which ticket, and what it cost. */
public record Result(String setup, int run, String ticketId, boolean pass, boolean categoryOk,
        boolean priorityOk, int promptTokens, int outputTokens, long latencyMillis,
        long computeMillis, String answer) {

    static final String CSV_HEADER =
            "setup;run;ticket;pass;categoryOk;priorityOk;promptTokens;outputTokens;latencyMillis;computeMillis;answer";

    String toCsv() {
        return String.join(";", setup, String.valueOf(run), ticketId, String.valueOf(pass),
                String.valueOf(categoryOk), String.valueOf(priorityOk), String.valueOf(promptTokens),
                String.valueOf(outputTokens), String.valueOf(latencyMillis), String.valueOf(computeMillis), answer);
    }

    static Result fromCsv(String line) {
        String[] f = line.split(";", 11);
        return new Result(f[0], Integer.parseInt(f[1]), f[2], Boolean.parseBoolean(f[3]),
                Boolean.parseBoolean(f[4]), Boolean.parseBoolean(f[5]), Integer.parseInt(f[6]),
                Integer.parseInt(f[7]), Long.parseLong(f[8]), Long.parseLong(f[9]), f[10]);
    }
}
