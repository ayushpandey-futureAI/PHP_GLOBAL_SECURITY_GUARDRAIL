//! Fastly Compute@Edge Security Pre-Filter for PHP Universal Vaccine
//! =================================================================
//! Compiles to WebAssembly (Wasm) for microsecond edge defense.

use fastly::http::{header, Method, StatusCode};
use fastly::{Error, Request, Response};
use regex::Regex;

#[fastly::main]
fn main(req: Request) -> Result<Response, Error> {
    // 1. Compile or initialize threat pattern heuristics
    let cgi_re = Regex::new(r"(?i)(?:-|%2d|%ad)[-\s]*(?:d|%64|%44)?\s*(?:allow_url_include|auto_prepend_file|disable_functions)").unwrap();
    let stream_re = Regex::new(r"(?i)(?:php|data|expect|phar)://").unwrap();
    let trav_re = Regex::new(r"(?i)(?:\.\.[/\\]|%2e%2e[/\\])").unwrap();

    let url_query = req.get_query_str().unwrap_or("");
    let url_path = req.get_path();

    // 2. Normalize Windows soft hyphen best-fit bypass
    let clean_query = url_query.replace("%ad", "-").replace("%AD", "-");

    // 3. Inspect Query & Path
    if cgi_re.is_match(&clean_query) || stream_re.is_match(&clean_query) || trav_re.is_match(url_path) {
        return Ok(Response::from_status(StatusCode::FORBIDDEN)
            .with_header("Content-Type", "text/plain")
            .with_header("X-Fastly-Protected-By", "PHP-Universal-Vaccine/1.3-Wasm")
            .with_body("403 Forbidden: Threat intercepted at Fastly Edge (Wasm Guardrail)\n"));
    }

    // 4. Pass clean traffic to origin backend
    let mut resp = req.send("origin_php_cluster")?;
    resp.set_header("X-Fastly-Protected-By", "PHP-Universal-Vaccine/1.3-Wasm");
    resp.set_header(header::X_CONTENT_TYPE_OPTIONS, "nosniff");
    resp.set_header(header::X_FRAME_OPTIONS, "SAMEORIGIN");

    Ok(resp)
}
