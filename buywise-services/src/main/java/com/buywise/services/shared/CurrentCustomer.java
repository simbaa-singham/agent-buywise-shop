package com.buywise.services.shared;

import org.springframework.http.HttpStatus;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.server.ResponseStatusException;

/**
 * Whose data a request may touch: the token's customer_id claim (ADR-050) - never a header, body or tool argument.
 * The claim comes from the Keycloak user attribute and survives every token swap.
 */
public final class CurrentCustomer {

    private CurrentCustomer() {
    }

    public static String id(Jwt token) {
        String id = token.getClaimAsString("customer_id");
        if (id == null || id.isBlank()) throw new ResponseStatusException(HttpStatus.FORBIDDEN, "No customer in this login");
        return id;
    }
}
