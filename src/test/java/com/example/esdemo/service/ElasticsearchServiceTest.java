package com.example.esdemo.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.json.jackson.JacksonJsonpMapper;
import co.elastic.clients.transport.ElasticsearchTransport;
import co.elastic.clients.transport.rest_client.RestClientTransport;
import com.example.esdemo.model.Product;
import org.apache.http.HttpHost;
import org.elasticsearch.client.RestClient;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.elasticsearch.ElasticsearchContainer;
import org.testcontainers.utility.DockerImageName;

import java.io.IOException;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class ElasticsearchServiceTest {

    private static ElasticsearchContainer container;
    private static RestClient restClient;
    private static ElasticsearchClient client;
    private static ElasticsearchService service;

    private static final String INDEX_NAME = "products";

    @BeforeAll
    static void startContainer() {
        // Setup Elasticsearch 7 container
        container = new ElasticsearchContainer(
                DockerImageName.parse("docker.elastic.co/elasticsearch/elasticsearch:7.17.10")
        ).withEnv("ES_JAVA_OPTS", "-Xms512m -Xmx512m");
        container.start();

        // Initialize RestClient and ElasticsearchClient pointing to the container's dynamic address
        restClient = RestClient.builder(
                HttpHost.create(container.getHttpHostAddress())
        ).build();

        ElasticsearchTransport transport = new RestClientTransport(
                restClient, new JacksonJsonpMapper()
        );

        client = new ElasticsearchClient(transport);
        service = new ElasticsearchService(client);
    }

    @AfterAll
    static void stopContainer() throws IOException {
        if (restClient != null) {
            restClient.close();
        }
        if (container != null) {
            container.stop();
        }
    }

    @BeforeEach
    void setUp() throws IOException {
        // Delete index if exists to ensure clean state
        service.deleteIndex(INDEX_NAME);
        service.createIndex(INDEX_NAME);
    }

    @Test
    void testIndexAndGetProduct() throws IOException {
        Product product = new Product("1", "Logitech MX Master 3S", "Wireless performance mouse", 99.99, "Electronics", 50);

        String indexedId = service.indexProduct(INDEX_NAME, product);
        assertEquals("1", indexedId);

        Optional<Product> retrieved = service.getProduct(INDEX_NAME, "1");
        assertTrue(retrieved.isPresent());
        assertEquals("Logitech MX Master 3S", retrieved.get().getName());
        assertEquals(99.99, retrieved.get().getPrice());
        assertEquals("Electronics", retrieved.get().getCategory());
    }

    @Test
    void testDeleteProduct() throws IOException {
        Product product = new Product("2", "Keychron K2", "Mechanical keyboard", 79.99, "Electronics", 30);
        service.indexProduct(INDEX_NAME, product);

        assertTrue(service.getProduct(INDEX_NAME, "2").isPresent());

        boolean deleted = service.deleteProduct(INDEX_NAME, "2");
        assertTrue(deleted);

        assertFalse(service.getProduct(INDEX_NAME, "2").isPresent());
    }

    @Test
    void testSearchProducts() throws IOException {
        Product p1 = new Product("101", "Apple MacBook Pro 14 Laptop", "M3 Chip Laptop", 1999.00, "Computers", 10);
        Product p2 = new Product("102", "Dell XPS 15 Laptop", "Intel i7 Laptop", 1799.00, "Computers", 15);
        Product p3 = new Product("103", "Sony WH-1000XM4 Headphones", "Noise Cancelling Headphones", 349.00, "Audio", 25);

        service.indexProduct(INDEX_NAME, p1);
        service.indexProduct(INDEX_NAME, p2);
        service.indexProduct(INDEX_NAME, p3);

        // Explicitly refresh the index to make documents searchable immediately
        client.indices().refresh(r -> r.index(INDEX_NAME));

        // Search for "Laptop"
        List<Product> laptops = service.searchProductsByName(INDEX_NAME, "Laptop");
        assertEquals(2, laptops.size());
        assertTrue(laptops.stream().anyMatch(p -> p.getName().contains("Apple")));
        assertTrue(laptops.stream().anyMatch(p -> p.getName().contains("Dell")));

        // Search for "Headphones"
        List<Product> headphones = service.searchProductsByName(INDEX_NAME, "Headphones");
        assertEquals(1, headphones.size());
        assertEquals("Sony WH-1000XM4 Headphones", headphones.get(0).getName());
    }
}
