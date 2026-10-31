package com.howtodoinjava.ai.thinking;

import java.util.List;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Short word problems with one numeric answer each, graded in code. */
public final class WordProblems {

    public record Problem(int id, String question, double answer) {
    }

    public static final List<Problem> ALL = List.of(
        new Problem(1, "A bakery bakes 7 trays of 24 muffins. It sells 150 muffins and gives away 9. How many muffins are left?", 9),
        new Problem(2, "A train travels 180 km in 2 hours, then 150 km in 3 hours. What is its average speed in km/h for the whole trip?", 66),
        new Problem(3, "A shirt costs 40 dollars. The price goes up by 25 percent, then the new price is cut by 20 percent. What is the final price in dollars?", 40),
        new Problem(4, "Tom is 3 times as old as his son. In 12 years, Tom will be twice as old as his son. How old is Tom now?", 36),
        new Problem(5, "A rectangle has a perimeter of 46 cm, and its length is 5 cm more than its width. What is its area in square cm?", 126),
        new Problem(6, "One pipe fills a tank in 6 hours and another fills it in 3 hours. How many hours do both pipes take together?", 2),
        new Problem(7, "3 notebooks and 2 pens cost 23 dollars. 2 notebooks and 3 pens cost 22 dollars. How many dollars does one notebook cost?", 5),
        new Problem(8, "How many whole numbers from 1 to 100 are divisible by 3 or by 5?", 47),
        new Problem(9, "5 workers build a wall in 12 days. How many days do 6 workers need for the same wall, working at the same rate?", 10),
        new Problem(10, "A store has 120 apples. On Monday it sells one third of them. On Tuesday it sells one quarter of the apples that are left. How many apples remain?", 60),
        new Problem(11, "The sum of three consecutive even numbers is 78. What is the largest of the three?", 28),
        new Problem(12, "A car uses 7 liters of fuel per 100 km, and fuel costs 2 dollars per liter. How many dollars does the fuel for a 350 km trip cost?", 49));

    private static final Pattern NUMBER = Pattern.compile("-?\\d[\\d,]*(?:\\.\\d+)?");

    private WordProblems() {
    }

    public static String prompt(Problem problem) {
        return problem.question() + "\nReply with the final answer as a number only.";
    }

    /** Takes the last number in the answer text; an empty answer is wrong. */
    public static boolean isCorrect(Problem problem, String content) {
        Matcher m = NUMBER.matcher(content);
        String last = null;
        while (m.find()) {
            last = m.group();
        }
        if (last == null) {
            return false;
        }
        double value = Double.parseDouble(last.replace(",", ""));
        return Math.abs(value - problem.answer()) < 1e-6;
    }
}
