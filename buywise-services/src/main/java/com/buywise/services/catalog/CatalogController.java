package com.buywise.services.catalog;

import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api/products")
class CatalogController {

    private final CatalogService catalog;

    CatalogController(CatalogService catalog) {
        this.catalog = catalog;
    }

    @GetMapping
    List<ProductSummary> search(@RequestParam(required = false) String q,
                                @RequestParam(required = false) String category,
                                @RequestParam(defaultValue = "5") int limit) {
        return catalog.search(q, category, Math.min(limit, 20));
    }

    @GetMapping("/{productId}")
    Product product(@PathVariable String productId) {
        return catalog.product(productId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown product " + productId));
    }
}
