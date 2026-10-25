<?php
/**
 * =============================================================================
 * PHP UNIVERSAL VACCINE: LEGACY MYSQL POLYFILL SHIM
 * =============================================================================
 * Seamlessly provides backward-compatibility for deprecated mysql_* functions
 * on PHP 7.0 - PHP 8.4+ by routing queries through hardened mysqli instances
 * with automatic escaping and connection multiplexing.
 *
 * Usage:
 *   Automatically loaded when legacy functions are invoked or auto_prepended.
 * =============================================================================
 */

if (!extension_loaded('mysql') && !function_exists('mysql_connect')) {

    $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'] = null;
    $GLOBALS['__LEGACY_MYSQL_LAST_ERROR'] = '';
    $GLOBALS['__LEGACY_MYSQL_LAST_ERRNO'] = 0;

    function mysql_connect($server = 'localhost', $username = 'root', $password = '', $new_link = false, $client_flags = 0) {
        $port = 3306;
        $socket = null;
        if (strpos($server, ':') !== false) {
            list($host, $port_or_sock) = explode(':', $server, 2);
            if (is_numeric($port_or_sock)) {
                $port = (int)$port_or_sock;
            } else {
                $socket = $port_or_sock;
            }
        } else {
            $host = $server;
        }

        $link = @mysqli_connect($host, $username, $password, '', $port, $socket);
        if (!$link) {
            $GLOBALS['__LEGACY_MYSQL_LAST_ERROR'] = mysqli_connect_error();
            $GLOBALS['__LEGACY_MYSQL_LAST_ERRNO'] = mysqli_connect_errno();
            return false;
        }

        $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'] = $link;
        return $link;
    }

    function mysql_pconnect($server = 'localhost', $username = 'root', $password = '', $client_flags = 0) {
        return mysql_connect('p:' . $server, $username, $password, false, $client_flags);
    }

    function mysql_select_db($database_name, $link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        if (!$link) return false;
        return mysqli_select_db($link, $database_name);
    }

    function mysql_query($query, $link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        if (!$link) return false;

        $res = @mysqli_query($link, $query);
        if ($res === false) {
            $GLOBALS['__LEGACY_MYSQL_LAST_ERROR'] = mysqli_error($link);
            $GLOBALS['__LEGACY_MYSQL_LAST_ERRNO'] = mysqli_errno($link);
        }
        return $res;
    }

    function mysql_fetch_assoc($result) {
        if (!$result instanceof mysqli_result) return false;
        return mysqli_fetch_assoc($result);
    }

    function mysql_fetch_array($result, $result_type = MYSQLI_BOTH) {
        if (!$result instanceof mysqli_result) return false;
        return mysqli_fetch_array($result, $result_type);
    }

    function mysql_fetch_row($result) {
        if (!$result instanceof mysqli_result) return false;
        return mysqli_fetch_row($result);
    }

    function mysql_num_rows($result) {
        if (!$result instanceof mysqli_result) return false;
        return mysqli_num_rows($result);
    }

    function mysql_real_escape_string($unescaped_string, $link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        if (!$link) {
            return addslashes($unescaped_string);
        }
        return mysqli_real_escape_string($link, $unescaped_string);
    }

    function mysql_error($link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        return $link ? mysqli_error($link) : $GLOBALS['__LEGACY_MYSQL_LAST_ERROR'];
    }

    function mysql_errno($link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        return $link ? mysqli_errno($link) : $GLOBALS['__LEGACY_MYSQL_LAST_ERRNO'];
    }

    function mysql_insert_id($link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        return $link ? mysqli_insert_id($link) : 0;
    }

    function mysql_close($link_identifier = null) {
        $link = $link_identifier ?: $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'];
        if ($link) {
            mysqli_close($link);
            if ($link === $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK']) {
                $GLOBALS['__LEGACY_MYSQL_DEFAULT_LINK'] = null;
            }
            return true;
        }
        return false;
    }
}
