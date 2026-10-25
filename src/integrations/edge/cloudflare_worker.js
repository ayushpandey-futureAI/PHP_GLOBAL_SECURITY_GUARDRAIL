/**
 * =============================================================================
 * CLOUDFLARE WORKERS EDGE SECURITY PRE-FILTER FOR PHP VACCINE
 * =============================================================================
 * Architecture: CDN Edge Ingress Defense (Cloudflare V8 Isolates)
 * Target: Neutralizes CVE-2024-4577, Deserialization, SSRF, and Web Shells
 *         at the global edge prior to origin server delivery.
 * Author: Ayush Pandey (ayushpandey-futureAI)
 * =============================================================================
 */

// Threat Pattern Signatures Matching schema/threat_signatures.json
const CGI_PARAM_RE = /(?:-|%2d|%ad)[-\s]*(?:d|%64|%44)?\s*(?:allow_url_include|auto_prepend_file|auto_append_file|disable_functions|open_basedir|cgi\.fix_pathinfo|safe_mode)/i;
const DESER_RE     = /(?:^|;|{|})([OaC]):\d+:"[^"]+":\d+:/i;
const STREAM_RE    = /(?:php|data|expect|phar|zip|glob|compress\.zlib|compress\.bzip2):\/\//i;
const TRAVERSAL_RE = /(?:\.\.[/\\]|%2e%2e[/\\]|\0|%00)/i;
const CMD_INJ_RE   = /(?:;|\|{1,2}|`|\$\()\s*(?:cat\s+\/etc|whoami|curl\s+[0-9a-z]|wget\s+[0-9a-z]|bash\s+-i|nc\s+-e|python\s+-c|id\b|uname\s+-a)/i;
const SQLI_RE      = /(?:\bUNION(?:\s+ALL)?\s+SELECT\b|\b(?:AND|OR)\s+(?:SLEEP|BENCHMARK|PG_SLEEP)\s*\(|\bSELECT\b.+\bFROM\b.+\bWHERE\b.+\b(?:SLEEP|BENCHMARK)\b|\b1=1\s*--|\bOR\s+['"]?1['"]?\s*=\s*['"]?1\b)/i;
const SSRF_RE      = /(?:https?:\/\/)?(?:169\.254\.169\.254|metadata\.google\.internal|100\.100\.100\.200|fd00:ec2::254)/i;

/**
 * Recursive Multi-Pass De-obfuscation Normalizer
 */
function deobfuscate(raw) {
  if (typeof raw !== 'string') return '';
  // 1. Normalize Windows soft hyphen best-fit character (%ad)
  let clean = raw.replace(/%(?:ad|AD)/g, '-');
  // 2. Decode multi-nested URL encoding
  let depth = 0;
  while (depth < 3) {
    try {
      const decoded = decodeURIComponent(clean.replace(/\+/g, ' '));
      if (decoded === clean) break;
      clean = decoded;
    } catch (e) {
      break;
    }
    depth++;
  }
  return clean;
}

/**
 * Payload Inspector returning [isBlocked, ThreatCategory]
 */
function inspect(str) {
  const c = deobfuscate(str);
  if (CGI_PARAM_RE.test(c)) return [true, 'CGI_ARGUMENT_INJECTION'];
  if (DESER_RE.test(c))     return [true, 'PHP_OBJECT_INJECTION'];
  if (STREAM_RE.test(c))    return [true, 'STREAM_WRAPPER_EXPLOITATION'];
  if (TRAVERSAL_RE.test(c)) return [true, 'PATH_TRAVERSAL_AND_POISONING'];
  if (CMD_INJ_RE.test(c))   return [true, 'COMMAND_INJECTION_AND_CHAINING'];
  if (SQLI_RE.test(c))      return [true, 'SQL_INJECTION'];
  if (SSRF_RE.test(c))      return [true, 'SERVER_SIDE_REQUEST_FORGERY'];
  return [false, 'CLEAN'];
}

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // 1. Inspect URL pathname and query parameters
    const [pathBlocked, pathThreat] = inspect(url.pathname);
    if (pathBlocked) {
      return generateBlockResponse(pathThreat, 'URL_PATH', request);
    }

    const [queryBlocked, queryThreat] = inspect(url.search);
    if (queryBlocked) {
      return generateBlockResponse(queryThreat, 'QUERY_STRING', request);
    }

    // 2. Inspect Cookies
    const cookieHeader = request.headers.get('Cookie') || '';
    const [cookieBlocked, cookieThreat] = inspect(cookieHeader);
    if (cookieBlocked) {
      return generateBlockResponse(cookieThreat, 'COOKIE', request);
    }

    // 3. Inspect Upload PHP file extensions in multipart/form paths
    if (/(?:uploads|files|wp-content\/uploads|media|storage)\/.*\.php$/i.test(url.pathname)) {
      return new Response('404 Not Found: Direct script execution disabled in upload directory', {
        status: 404,
        headers: { 'Content-Type': 'text/plain', 'X-Protected-By': 'PHP-Universal-Vaccine-Edge/1.3' }
      });
    }

    // 4. Forward Clean Request to Origin Server
    const response = await fetch(request);

    // 5. Inject Edge Security Headers on Outgoing Response
    const newHeaders = new Headers(response.headers);
    newHeaders.set('X-Edge-Protected-By', 'PHP-Universal-Vaccine-Edge/1.3');
    newHeaders.set('X-Content-Type-Options', 'nosniff');
    newHeaders.set('X-Frame-Options', 'SAMEORIGIN');

    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: newHeaders
    });
  }
};

function generateBlockResponse(threatCategory, sourceLocation, request) {
  const clientIP = request.headers.get('CF-Connecting-IP') || 'UNKNOWN';
  console.log(`[EDGE_THREAT_BLOCKED] Cat: ${threatCategory} | Src: ${sourceLocation} | IP: ${clientIP} | URI: ${request.url}`);

  return new Response(`403 Forbidden: Malicious payload intercepted at Cloudflare Edge [Threat: ${threatCategory}]\n`, {
    status: 403,
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'X-Edge-Protected-By': 'PHP-Universal-Vaccine-Edge/1.3',
      'X-Threat-Category': threatCategory
    }
  });
}
