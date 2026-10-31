package com.howtodoinjava.peopledesk;

import java.util.List;
import java.util.Set;

public record Answer(Route route, String text, Set<String> citations,
                     List<String> retrieved, SensitiveTopic topic) {

    public enum Route { ANSWERED, REFUSED, ESCALATED }
}
