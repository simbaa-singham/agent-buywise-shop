package com.buywise.services.shared;

import static org.springframework.security.authorization.AuthorityAuthorizationManager.hasAuthority;
import static org.springframework.security.authorization.AuthorityAuthorizationManager.hasRole;
import static org.springframework.security.authorization.AuthorizationManagers.allOf;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.oauth2.core.DelegatingOAuth2TokenValidator;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtClaimValidator;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.security.oauth2.jwt.JwtValidators;
import org.springframework.security.oauth2.jwt.NimbusJwtDecoder;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;
import org.springframework.security.oauth2.server.resource.web.authentication.BearerTokenAuthenticationFilter;
import org.springframework.security.web.SecurityFilterChain;

/**
 * buywise-services as an OAuth resource server (ADR-050). Every request needs a Keycloak token issued by our realm
 * for the audience buywise-services - in practice one MCP swapped for a single scope. Each endpoint needs:
 * scope = what the calling app may do, role customer = what the user is, and (in the controllers) the token's
 * customer_id = whose data. Only the health check is open.
 */
@Configuration
class SecurityConfig {

    @Bean
    SecurityFilterChain api(HttpSecurity http, JwtDecoder decoder) throws Exception {
        var ordersRead = allOf(hasAuthority("SCOPE_orders:read"), hasRole("customer"));
        var ordersWrite = allOf(hasAuthority("SCOPE_orders:write"), hasRole("customer"));
        http.authorizeHttpRequests(a -> a
                        .requestMatchers("/actuator/health", "/actuator/health/**").permitAll()
                        .requestMatchers(HttpMethod.GET, "/api/products", "/api/products/**").hasAuthority("SCOPE_catalog:read")
                        .requestMatchers(HttpMethod.GET, "/api/stores", "/api/stores/**", "/api/stock")
                                .hasAuthority("SCOPE_inventory:read")
                        .requestMatchers(HttpMethod.POST, "/api/orders/quote").access(ordersRead)
                        .requestMatchers(HttpMethod.GET, "/api/orders", "/api/orders/**").access(ordersRead)
                        .requestMatchers(HttpMethod.POST, "/api/orders", "/api/orders/*/cancel").access(ordersWrite)
                        .requestMatchers(HttpMethod.GET, "/api/customers/me").hasRole("customer")
                        .anyRequest().denyAll())
                .oauth2ResourceServer(o -> o.jwt(j -> j.decoder(decoder).jwtAuthenticationConverter(authorities())))
                .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .csrf(c -> c.disable())  // no cookies, no browser: tokens only
                .addFilterAfter(new AuditFilter(), BearerTokenAuthenticationFilter.class);
        return http.build();
    }

    /** Checks signature (Keycloak keys), issuer, expiry and audience. */
    @Bean
    JwtDecoder jwtDecoder(@Value("${buywise.security.issuer}") String issuer,
                          @Value("${buywise.security.jwks-uri:}") String jwksUri,
                          @Value("${buywise.security.audience}") String audience) {
        String keys = jwksUri.isBlank() ? issuer + "/protocol/openid-connect/certs" : jwksUri;
        NimbusJwtDecoder decoder = NimbusJwtDecoder.withJwkSetUri(keys).build();
        decoder.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
                JwtValidators.createDefaultWithIssuer(issuer),
                new JwtClaimValidator<List<String>>("aud", aud -> aud != null && aud.contains(audience))));
        return decoder;
    }

    /** Scopes become SCOPE_x, Keycloak realm roles (realm_access.roles) become ROLE_x. */
    private static JwtAuthenticationConverter authorities() {
        var scopes = new JwtGrantedAuthoritiesConverter();
        var converter = new JwtAuthenticationConverter();
        converter.setJwtGrantedAuthoritiesConverter(jwt -> {
            Collection<GrantedAuthority> all = new ArrayList<>(scopes.convert(jwt));
            all.addAll(realmRoles(jwt));
            return all;
        });
        return converter;
    }

    private static List<GrantedAuthority> realmRoles(Jwt jwt) {
        Map<String, Object> realm = jwt.getClaimAsMap("realm_access");
        if (realm == null || !(realm.get("roles") instanceof List<?> roles)) return List.of();
        return roles.stream().map(r -> (GrantedAuthority) new SimpleGrantedAuthority("ROLE_" + r)).toList();
    }
}
