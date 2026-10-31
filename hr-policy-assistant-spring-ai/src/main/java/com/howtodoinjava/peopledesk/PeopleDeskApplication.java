package com.howtodoinjava.peopledesk;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.ConfigurationPropertiesScan;
import org.springframework.context.ConfigurableApplicationContext;

@SpringBootApplication
@ConfigurationPropertiesScan
public class PeopleDeskApplication {

    public static void main(String[] args) {
        ConfigurableApplicationContext context = SpringApplication.run(PeopleDeskApplication.class, args);
        // the command-line runners are done; exit even if a library left non-daemon threads running
        // (RetrievalAugmentationAdvisor creates its own thread pool, used in the demo)
        if (context.getEnvironment().matchesProfiles("probe | eval | demo")) {
            System.exit(SpringApplication.exit(context));
        }
    }
}
