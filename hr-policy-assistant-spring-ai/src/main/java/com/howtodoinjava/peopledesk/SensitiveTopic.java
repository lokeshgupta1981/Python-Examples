package com.howtodoinjava.peopledesk;

public enum SensitiveTopic {
    HARASSMENT, DISCRIMINATION, HEALTH, GRIEVANCE, LEGAL, NONE;

    /** Anything the model returns that isn't one of the names is treated as sensitive. */
    public static SensitiveTopic parse(String modelOutput) {
        String word = modelOutput == null ? "" : modelOutput.strip().split("\\W+")[0].toUpperCase();
        for (SensitiveTopic topic : values()) {
            if (topic.name().equals(word)) {
                return topic;
            }
        }
        return GRIEVANCE;
    }
}
