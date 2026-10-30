package com.howtodoinjava.ai.replies;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.reader.markdown.MarkdownDocumentReader;
import org.springframework.ai.reader.markdown.config.MarkdownDocumentReaderConfig;
import org.springframework.ai.vectorstore.SimpleVectorStore;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.ResourcePatternResolver;

@Configuration
public class HelpIndexConfig {

    private static final Logger log = LoggerFactory.getLogger(HelpIndexConfig.class);

    @Bean
    SimpleVectorStore helpIndex(EmbeddingModel embeddingModel, ReplyProperties props,
                                ResourcePatternResolver resolver) throws IOException {
        SimpleVectorStore store = SimpleVectorStore.builder(embeddingModel).build();
        File indexFile = new File(props.indexFile());
        if (indexFile.exists()) {
            store.load(indexFile); // no embedding calls
            log.info("Loaded help index from {}", indexFile.getAbsolutePath());
            return store;
        }
        List<Document> articles = readArticles(props, resolver);
        store.add(articles); // one embedding per article
        store.save(indexFile);
        log.info("Indexed {} help articles into {}", articles.size(), indexFile.getAbsolutePath());
        return store;
    }

    List<Document> readArticles(ReplyProperties props,
                                ResourcePatternResolver resolver) throws IOException {
        List<Document> articles = new ArrayList<>();
        for (Resource file : resolver.getResources(props.helpCenter())) {
            String name = file.getFilename(); // A01-return-window.md
            String articleId = name.substring(0, 3);
            String slug = name.substring(4, name.length() - ".md".length());

            MarkdownDocumentReaderConfig config = MarkdownDocumentReaderConfig.builder()
                    .withAdditionalMetadata(Map.of(
                            "articleId", articleId,
                            "url", props.articleBaseUrl() + slug))
                    .build();
            articles.addAll(new MarkdownDocumentReader(file, config).get());
        }
        return articles;
    }
}
