package com.howtodoinjava.peopledesk;

import java.util.ArrayList;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Profile;
import org.springframework.stereotype.Component;

import com.howtodoinjava.peopledesk.Answer.Route;

/** Runs the labelled questions and reports routing and citation accuracy. */
@Component
@Profile("eval")
public class Evaluation implements CommandLineRunner {

    private final PolicyAssistant assistant;

    public Evaluation(PolicyAssistant assistant) {
        this.assistant = assistant;
    }

    @Override
    public void run(String... args) throws Exception {
        Map<Route, List<Double>> seconds = new EnumMap<>(Route.class);
        Map<Route, int[]> routed = new EnumMap<>(Route.class);   // [correct, total]
        int citedRight = 0;
        int answerable = 0;

        for (LabelledQuestion q : LabelledQuestion.load()) {
            long start = System.nanoTime();
            Answer a = assistant.ask(q.question(), q.employee(), q.asOf());
            double s = (System.nanoTime() - start) / 1e9;

            Route expected = q.expectedRoute();
            boolean routeOk = a.route() == expected;
            routed.computeIfAbsent(expected, r -> new int[2])[1]++;
            if (routeOk) {
                routed.get(expected)[0]++;
            }
            seconds.computeIfAbsent(expected, r -> new ArrayList<>()).add(s);
            if (expected == Route.ANSWERED) {
                answerable++;
                if (a.citations().contains(q.expectedSection())) {
                    citedRight++;
                }
            }
            System.out.printf("%s %s/%s expected=%s actual=%s topic=%s %.1fs%n  retrieved=%s%n  cited=%s%n  %s%n",
                    q.id(), q.employee().region(), q.employee().employeeType(), expected, a.route(),
                    a.topic(), s, a.retrieved(), a.citations(), a.text().replace('\n', ' '));
        }

        System.out.println();
        for (Route r : Route.values()) {
            int[] c = routed.get(r);
            List<Double> t = seconds.get(r).stream().sorted().toList();
            double median = t.size() % 2 == 1 ? t.get(t.size() / 2)
                    : (t.get(t.size() / 2 - 1) + t.get(t.size() / 2)) / 2;
            System.out.printf("%-9s correct route %d/%d, median %.1fs%n", r, c[0], c[1], median);
        }
        System.out.printf("Expected section cited: %d/%d%n", citedRight, answerable);
    }
}
