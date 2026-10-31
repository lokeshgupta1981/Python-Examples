package com.howtodoinjava.peopledesk;

import java.io.IOException;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class PeopleDeskConfig {

    @Bean
    SimpleVectorStore policyStore(EmbeddingModel embeddingModel) throws IOException {
        SimpleVectorStore store = SimpleVectorStore.builder(embeddingModel).build();
        store.add(new PolicyLoader().load("classpath:policies/*.md"));
        return store;
    }

    @Bean
    SensitiveTopicClassifier sensitiveTopicClassifier(ChatClient.Builder builder) {
        return new SensitiveTopicClassifier(builder.clone());
    }

    @Bean
    PolicyAssistant policyAssistant(SensitiveTopicClassifier classifier, SimpleVectorStore store,
                                    ChatClient.Builder builder, PeopleDeskProperties props) {
        return new PolicyAssistant(classifier, store, builder.clone(), props);
    }
}
