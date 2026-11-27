package com.buywise.services.shared;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * One audit line per API request (ADR-050 amendment): who (sub, customer_id), through which client (azp), what
 * (method, path), result (status). Keycloak issues no act claim, so this line per hop - joined by the trace id
 * later (ADR-063) - is the "who acted for whom" chain.
 */
class AuditFilter extends OncePerRequestFilter {

    private static final Logger AUDIT = LoggerFactory.getLogger("buywise.audit");

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain chain)
            throws ServletException, IOException {
        try {
            chain.doFilter(request, response);
        } finally {
            if (request.getRequestURI().startsWith("/api/")) {
                String sub = null, customer = null, azp = null;
                if (SecurityContextHolder.getContext().getAuthentication() instanceof JwtAuthenticationToken t) {
                    sub = t.getToken().getSubject();
                    customer = t.getToken().getClaimAsString("customer_id");
                    azp = t.getToken().getClaimAsString("azp");
                }
                AUDIT.info("{\"event\":\"request\",\"client\":\"buywise-services\",\"method\":\"{}\",\"path\":\"{}\","
                                + "\"status\":{},\"sub\":{},\"customer_id\":{},\"azp\":{}}",
                        request.getMethod(), request.getRequestURI(), response.getStatus(),
                        quote(sub), quote(customer), quote(azp));
            }
        }
    }

    private static String quote(String v) {
        return v == null ? "null" : "\"" + v.replace("\"", "") + "\"";
    }
}
