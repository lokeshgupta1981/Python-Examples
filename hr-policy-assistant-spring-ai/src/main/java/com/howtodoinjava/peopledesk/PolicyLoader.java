package com.howtodoinjava.peopledesk;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.document.Document;
import org.springframework.ai.reader.markdown.MarkdownDocumentReader;
import org.springframework.ai.reader.markdown.config.MarkdownDocumentReaderConfig;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;

public class PolicyLoader {

    private static final Logger log = LoggerFactory.getLogger(PolicyLoader.class);
    private static final Pattern SECTION = Pattern.compile("(\\d+\\.\\d+)\\s+(.+)");

    public List<Document> load(String locationPattern) throws IOException {
        Resource[] files = new PathMatchingResourcePatternResolver().getResources(locationPattern);
        List<Document> sections = new ArrayList<>();
        Map<String, Integer> perPolicy = new TreeMap<>();
        for (Resource file : files) {
            List<Document> fileSections = loadFile(file);
            sections.addAll(fileSections);
            Document first = fileSections.getFirst();
            perPolicy.merge(first.getMetadata().get("policy") + " v" + first.getMetadata().get("version"),
                    fileSections.size(), Integer::sum);
        }
        perPolicy.forEach((policy, count) -> log.info("Loaded {} sections from {}", count, policy));
        return sections;
    }

    List<Document> loadFile(Resource file) throws IOException {
        FrontMatter frontMatter = FrontMatter.parse(file.getContentAsString(StandardCharsets.UTF_8));
        var config = MarkdownDocumentReaderConfig.builder()
                .withAdditionalMetadata(frontMatter.metadata())
                .build();
        var body = new ByteArrayResource(frontMatter.body().getBytes(StandardCharsets.UTF_8));
        List<Document> sections = new ArrayList<>();
        for (Document doc : new MarkdownDocumentReader(body, config).get()) {
            // the reader puts the heading text in "title"; the paragraph is the document text
            Matcher m = SECTION.matcher(String.valueOf(doc.getMetadata().get("title")));
            if (!m.matches()) {
                continue; // text outside a numbered section
            }
            Map<String, Object> metadata = new HashMap<>(doc.getMetadata());
            metadata.put("section", m.group(1));
            metadata.put("section_title", m.group(2));
            sections.add(Document.builder()
                    .text(m.group(2) + ": " + doc.getText())
                    .metadata(metadata)
                    .build());
        }
        return sections;
    }

    public static String label(Document doc) {
        Map<String, Object> m = doc.getMetadata();
        return m.get("policy") + " v" + m.get("version") + ", " + m.get("section");
    }
}
