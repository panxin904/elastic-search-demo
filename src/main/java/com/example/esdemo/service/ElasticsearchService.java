package com.example.esdemo.service;

import co.elastic.clients.elasticsearch.ElasticsearchClient;
import co.elastic.clients.elasticsearch.core.*;
import co.elastic.clients.elasticsearch.core.search.Hit;
import co.elastic.clients.elasticsearch.indices.CreateIndexResponse;
import co.elastic.clients.elasticsearch.indices.DeleteIndexResponse;
import co.elastic.clients.elasticsearch.indices.ExistsRequest;
import com.example.esdemo.model.Product;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class ElasticsearchService {

    private static final Logger logger = LoggerFactory.getLogger(ElasticsearchService.class);
    private final ElasticsearchClient client;

    public ElasticsearchService(ElasticsearchClient client) {
        this.client = client;
    }

    /**
     * Create an index if it doesn't already exist.
     */
    public boolean createIndex(String indexName) throws IOException {
        boolean exists = client.indices().exists(ExistsRequest.of(e -> e.index(indexName))).value();
        if (exists) {
            logger.info("Index '{}' already exists.", indexName);
            return false;
        }

        CreateIndexResponse response = client.indices().create(c -> c.index(indexName));
        logger.info("Created index '{}'. Acknowledged: {}", indexName, response.acknowledged());
        return response.acknowledged();
    }

    /**
     * Delete an index.
     */
    public boolean deleteIndex(String indexName) throws IOException {
        boolean exists = client.indices().exists(ExistsRequest.of(e -> e.index(indexName))).value();
        if (!exists) {
            logger.info("Index '{}' does not exist, skipping deletion.", indexName);
            return false;
        }

        DeleteIndexResponse response = client.indices().delete(d -> d.index(indexName));
        logger.info("Deleted index '{}'. Acknowledged: {}", indexName, response.acknowledged());
        return response.acknowledged();
    }

    /**
     * Index a product document.
     */
    public String indexProduct(String indexName, Product product) throws IOException {
        IndexRequest<Product> request = IndexRequest.of(i -> i
                .index(indexName)
                .id(product.getId())
                .document(product)
        );

        IndexResponse response = client.index(request);
        logger.info("Indexed product with ID: {}. Result: {}", response.id(), response.result());
        return response.id();
    }

    /**
     * Retrieve a product document by ID.
     */
    public Optional<Product> getProduct(String indexName, String id) throws IOException {
        GetRequest getRequest = GetRequest.of(g -> g
                .index(indexName)
                .id(id)
        );

        GetResponse<Product> response = client.get(getRequest, Product.class);
        if (response.found()) {
            return Optional.ofNullable(response.source());
        }
        return Optional.empty();
    }

    /**
     * Delete a product document by ID.
     */
    public boolean deleteProduct(String indexName, String id) throws IOException {
        DeleteRequest deleteRequest = DeleteRequest.of(d -> d
                .index(indexName)
                .id(id)
        );

        DeleteResponse response = client.delete(deleteRequest);
        logger.info("Deleted product with ID: {}. Result: {}", response.id(), response.result());
        return "deleted".equalsIgnoreCase(response.result().name()) || "not_found".equalsIgnoreCase(response.result().name());
    }

    /**
     * Search products by name (fuzzy search).
     */
    public List<Product> searchProductsByName(String indexName, String nameQuery) throws IOException {
        SearchRequest searchRequest = SearchRequest.of(s -> s
                .index(indexName)
                .query(q -> q
                        .match(m -> m
                                .field("name")
                                .query(nameQuery)
                        )
                )
        );

        SearchResponse<Product> response = client.search(searchRequest, Product.class);
        List<Product> products = new ArrayList<>();
        for (Hit<Product> hit : response.hits().hits()) {
            if (hit.source() != null) {
                products.add(hit.source());
            }
        }
        logger.info("Found {} products matching name: '{}'", products.size(), nameQuery);
        return products;
    }
}
