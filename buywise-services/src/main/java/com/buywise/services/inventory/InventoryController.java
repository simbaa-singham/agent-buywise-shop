package com.buywise.services.inventory;

import java.util.List;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping("/api")
class InventoryController {

    private final InventoryService inventory;

    InventoryController(InventoryService inventory) {
        this.inventory = inventory;
    }

    @GetMapping("/stores")
    List<Store> stores() {
        return inventory.stores();
    }

    @GetMapping("/stores/{storeId}")
    Store store(@PathVariable String storeId) {
        return inventory.store(storeId)
                .orElseThrow(() -> new ResponseStatusException(HttpStatus.NOT_FOUND, "Unknown store " + storeId));
    }

    @GetMapping("/stock")
    List<StockLevel> stock(@RequestParam List<String> skus, @RequestParam(required = false) String storeId) {
        return inventory.stock(skus, storeId);
    }
}
