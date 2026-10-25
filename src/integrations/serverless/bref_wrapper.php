<?php
/**
 * =============================================================================
 * AWS LAMBDA & BREF SERVERLESS RUNTIME INOCULATION WRAPPER
 * =============================================================================
 * Architecture: Zero-Touch Ambient Function Middleware for Serverless PHP
 * Platform: AWS Lambda (API Gateway v1/v2, Application Load Balancer, Bref)
 * Target: Intercepts event parameters, query strings, and body payloads before
 *         userland Bref Lambda handlers execute.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */

require_once __DIR__ . '/../../vaccine.php';

class BrefVaccineGuardrail {

    /**
     * Wrap any Bref Lambda Handler with the Universal Vaccine RASP inspection
     *
     * Usage:
     * return BrefVaccineGuardrail::wrap(function ($event, $context) {
     *     return ['statusCode' => 200, 'body' => 'Hello World'];
     * });
     */
    public static function wrap(callable $downstreamHandler) {
        return function ($event, $context) use ($downstreamHandler) {
            $threat = self::inspectLambdaEvent($event);
            if ($threat !== null) {
                return self::generateBlockedResponse($threat, $event);
            }
            return $downstreamHandler($event, $context);
        };
    }

    /**
     * Inspects AWS API Gateway v1/v2 or ALB event structures
     */
    public static function inspectLambdaEvent($event) {
        if (!is_array($event)) {
            return null;
        }

        // 1. Inspect Query String Parameters
        if (isset($event['queryStringParameters']) && is_array($event['queryStringParameters'])) {
            foreach ($event['queryStringParameters'] as $key => $val) {
                $nodeVal = $val;
                _vaccine_inspect_node($nodeVal, $key);
            }
        }

        // 2. Inspect Multi-Value Query String Parameters
        if (isset($event['multiValueQueryStringParameters']) && is_array($event['multiValueQueryStringParameters'])) {
            foreach ($event['multiValueQueryStringParameters'] as $key => $vals) {
                if (is_array($vals)) {
                    foreach ($vals as $v) {
                        $nodeVal = $v;
                        _vaccine_inspect_node($nodeVal, $key);
                    }
                }
            }
        }

        // 3. Inspect Raw Query String (API Gateway v2)
        if (isset($event['rawQueryString']) && is_string($event['rawQueryString'])) {
            $nodeVal = $event['rawQueryString'];
            _vaccine_inspect_node($nodeVal, 'rawQueryString');
        }

        // 4. Inspect Request Body (JSON or Form-URLEncoded)
        if (isset($event['body']) && is_string($event['body'])) {
            $body = $event['body'];
            if (!empty($event['isBase64Encoded'])) {
                $body = base64_decode($body);
            }

            // Quick scan of raw body
            $nodeVal = $body;
            _vaccine_inspect_node($nodeVal, 'body');

            // If JSON body, unpack and inspect nodes recursively
            $json = json_decode($body, true);
            if (is_array($json)) {
                array_walk_recursive($json, '_vaccine_inspect_node');
            }
        }

        // 5. Inspect Cookies
        if (isset($event['cookies']) && is_array($event['cookies'])) {
            foreach ($event['cookies'] as $cookieStr) {
                $nodeVal = $cookieStr;
                _vaccine_inspect_node($nodeVal, 'cookie');
            }
        }

        return null;
    }

    /**
     * Emits standard HTTP 403 response compliant with API Gateway v1, v2 and ALB
     */
    public static function generateBlockedResponse($threatId, $event) {
        $requestId = isset($event['requestContext']['requestId']) ? $event['requestContext']['requestId'] : 'local-invocation';
        
        // Emit structured CloudWatch log line
        $logEntry = json_encode([
            'source'       => 'AWS_LAMBDA_PHP_VACCINE',
            'requestId'    => $requestId,
            'threat_id'    => $threatId,
            'action'       => 'BLOCKED',
            'timestamp'    => date('c')
        ]);
        error_log($logEntry);

        return [
            'statusCode' => 403,
            'headers'    => [
                'Content-Type'    => 'text/plain; charset=utf-8',
                'X-Protected-By'  => 'PHP-Universal-Vaccine/1.3-Serverless',
                'X-Threat-Id'     => $threatId
            ],
            'body'       => "403 Forbidden: Malicious payload intercepted by Serverless PHP Runtime Vaccine [RequestId: {$requestId}]\n"
        ];
    }
}
