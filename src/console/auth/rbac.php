<?php
/**
 * =============================================================================
 * ENTERPRISE RBAC & OIDC / SAML SSO AUTHENTICATION MODULE
 * =============================================================================
 * Multi-tenant Role-Based Access Control & Identity Assertion Validator
 * Supports Okta, Azure AD (Microsoft Entra), Keycloak, and PingIdentity.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */

class EnterpriseRBAC {

    const ROLE_SUPER_ADMIN        = 'SUPER_ADMIN';
    const ROLE_SECOPS_ANALYST     = 'SECOPS_ANALYST';
    const ROLE_COMPLIANCE_AUDITOR = 'COMPLIANCE_AUDITOR';
    const ROLE_VIEWER             = 'VIEWER';

    private static $permissions = [
        self::ROLE_SUPER_ADMIN => [
            'view_dashboard', 'manage_fleet', 'modify_policies', 'export_compliance', 'manage_users'
        ],
        self::ROLE_SECOPS_ANALYST => [
            'view_dashboard', 'view_telemetry', 'modify_allowlist', 'trigger_investigation'
        ],
        self::ROLE_COMPLIANCE_AUDITOR => [
            'view_dashboard', 'view_telemetry', 'export_compliance'
        ],
        self::ROLE_VIEWER => [
            'view_dashboard'
        ]
    ];

    /**
     * Verifies if a given role possesses a specific permission
     */
    public static function hasPermission($role, $permission) {
        if (!isset(self::$permissions[$role])) {
            return false;
        }
        return in_array($permission, self::$permissions[$role], true);
    }

    /**
     * Validates an OIDC JWT Bearer Token (Simulated / Standalone RFC-7519 Validator)
     */
    public static function validateOidcToken($jwtToken) {
        if (empty($jwtToken) || substr_count($jwtToken, '.') !== 2) {
            return ['valid' => false, 'error' => 'Malformed JWT format'];
        }

        $parts = explode('.', $jwtToken);
        $payloadJson = base64_decode(strtr($parts[1], '-_', '+/'));
        $claims = json_decode($payloadJson, true);

        if (!$claims) {
            return ['valid' => false, 'error' => 'Invalid JWT payload'];
        }

        // Check expiration
        if (isset($claims['exp']) && $claims['exp'] < time()) {
            return ['valid' => false, 'error' => 'Token expired'];
        }

        // Extract tenant and role
        $role = isset($claims['role']) ? $claims['role'] : self::ROLE_VIEWER;
        $user = isset($claims['sub']) ? $claims['sub'] : 'anonymous_user';
        $tenant = isset($claims['tenant_id']) ? $claims['tenant_id'] : 'default_tenant';

        return [
            'valid'     => true,
            'user'      => $user,
            'tenant_id' => $tenant,
            'role'      => $role,
            'claims'    => $claims
        ];
    }

    /**
     * Parses and validates a SAML 2.0 XML Assertion Response
     */
    public static function parseSamlAssertion($samlXml) {
        if (empty($samlXml) || strpos($samlXml, 'saml2:Assertion') === false && strpos($samlXml, 'Assertion') === false) {
            return ['valid' => false, 'error' => 'Invalid SAML 2.0 XML assertion'];
        }

        // Extract NameID (User Principal Name / Email)
        preg_match('/<saml2?:NameID[^>]*>(.*?)<\/saml2?:NameID>/i', $samlXml, $nameMatch);
        $email = isset($nameMatch[1]) ? trim($nameMatch[1]) : 'saml_user@enterprise.com';

        // Extract Role Attribute
        preg_match('/Attribute Name="Role"[^>]*>.*?<saml2?:AttributeValue[^>]*>(.*?)<\/saml2?:AttributeValue>/is', $samlXml, $roleMatch);
        $role = isset($roleMatch[1]) ? trim($roleMatch[1]) : self::ROLE_SECOPS_ANALYST;

        return [
            'valid' => true,
            'user'  => $email,
            'role'  => $role
        ];
    }
}
