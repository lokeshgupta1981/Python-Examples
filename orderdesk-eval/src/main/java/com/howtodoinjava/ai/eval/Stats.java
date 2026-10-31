package com.howtodoinjava.ai.eval;

import java.util.List;

public final class Stats {

    private Stats() {
    }

    /** Half-width of the 95% confidence interval for an accuracy p measured on n items. */
    public static double marginOfError(double p, int n) {
        return 1.96 * Math.sqrt(p * (1 - p) / n);
    }

    /** Value below which the given fraction of the sorted values fall (nearest rank). */
    public static long percentile(List<Long> values, double fraction) {
        List<Long> sorted = values.stream().sorted().toList();
        int rank = (int) Math.ceil(fraction * sorted.size());
        return sorted.get(Math.max(0, rank - 1));
    }
}
