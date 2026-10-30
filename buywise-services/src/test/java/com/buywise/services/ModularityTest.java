package com.buywise.services;

import org.junit.jupiter.api.Test;
import org.springframework.modulith.core.ApplicationModules;

/** Fails if a module reaches into another module's internals (ADR-014). */
class ModularityTest {

    @Test
    void modulesRespectBoundaries() {
        ApplicationModules.of(BuywiseServicesApplication.class).verify();
    }
}
