package com.buywise.services.catalog;

import java.util.Arrays;
import java.util.Collection;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.function.Function;
import java.util.stream.Collectors;
import org.springframework.jdbc.core.simple.JdbcClient;
import org.springframework.stereotype.Service;

/** Catalog module API: products, variants and prices. Availability is sale status only (ADR-043). */
@Service
public class CatalogService {

    private static final String SUMMARY_SQL = """
            SELECT p.product_id, p.category, p.family, p.model, p.availability, p.release_date,
                   min(v.list_price) AS from_price
            FROM catalog.products p JOIN catalog.variants v USING (product_id)
            GROUP BY p.product_id""";

    private static final String VARIANT_SQL = """
            SELECT v.sku, v.product_id, p.model, p.availability, v.storage_gb, v.size, v.color, v.list_price
            FROM catalog.variants v JOIN catalog.products p USING (product_id)""";

    private final JdbcClient jdbc;

    CatalogService(JdbcClient jdbc) {
        this.jdbc = jdbc;
    }

    /** Ranks products by how many query words match model, family or category; ties go to the shorter model name. */
    public List<ProductSummary> search(String query, String category, int limit) {
        List<ProductSummary> all = jdbc.sql(SUMMARY_SQL).query(ProductSummary.class).list();
        List<String> words = query == null ? List.of()
                : Arrays.stream(query.toLowerCase(Locale.ROOT).split("[^a-z0-9]+")).filter(w -> !w.isBlank()).toList();
        return all.stream()
                .filter(p -> category == null || category.isBlank() || p.category().equalsIgnoreCase(category))
                .map(p -> Map.entry(p, score(p, words)))
                .filter(e -> words.isEmpty() || e.getValue() > 0)
                .sorted(Comparator.<Map.Entry<ProductSummary, Integer>>comparingInt(Map.Entry::getValue).reversed()
                        .thenComparingInt(e -> e.getKey().model().length()))
                .limit(limit)
                .map(Map.Entry::getKey)
                .toList();
    }

    private static int score(ProductSummary p, List<String> words) {
        String text = (p.model() + " " + p.family() + " " + p.category()).toLowerCase(Locale.ROOT);
        List<String> tokens = Arrays.asList(text.split("[^a-z0-9]+"));
        return (int) words.stream().filter(tokens::contains).count();
    }

    public Optional<Product> product(String productId) {
        record Row(String productId, String category, String family, String model, String availability,
                   java.time.LocalDate releaseDate, String specs, String compatibilityNote) {}
        return jdbc.sql("""
                        SELECT product_id, category, family, model, availability, release_date,
                               specs::text AS specs, compatibility_note
                        FROM catalog.products WHERE product_id = ?""")
                .param(productId).query(Row.class).optional()
                .map(r -> new Product(r.productId(), r.category(), r.family(), r.model(), r.availability(),
                        r.releaseDate(), r.specs(), r.compatibilityNote(),
                        jdbc.sql(VARIANT_SQL + " WHERE v.product_id = ? ORDER BY v.list_price, v.sku")
                                .param(productId).query(Variant.class).list()));
    }

    public Map<String, Variant> variants(Collection<String> skus) {
        if (skus.isEmpty()) return Map.of();
        return jdbc.sql(VARIANT_SQL + " WHERE v.sku IN (:skus)").param("skus", skus)
                .query(Variant.class).list().stream()
                .collect(Collectors.toMap(Variant::sku, Function.identity()));
    }
}
