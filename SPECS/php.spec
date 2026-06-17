# Fedora spec file for php
#
# License: MIT
# http://opensource.org/licenses/MIT
#
# Please preserve changelog entries
#
# API/ABI check

%define _debugsource_template %{nil}
%define debug_package %{nil}

# by default all features are enabled
%global with_cli 0%{!?_without_cli:1}
%global with_xml 0%{!?_without_xml:1}
%global with_pgsql 0%{!?_without_pgsql:1}
%global with_odbc 0%{!?_without_odbc:1}
%global with_ldap 0%{!?_without_ldap:1}
%global with_bcmath 0%{!?_without_bcmath:1}
%global with_posix 0%{!?_without_posix:1}
%global with_sodium 0%{!?_without_sodium:1}
%global with_ffi 0%{!?_without_ffi:1}
%global with_tidy 0%{!?_without_tidy:1}
%global with_sockets 0%{!?_without_sockets:1}
%global with_devel 0%{!?_without_devel:1}
%global with_common 0%{!?_without_common:1}

# we do not know for sure if any of shared module enabled
%global with_modules 0

# https://github.com/rpm-software-management/rpm/blob/master/doc/manual/conditionalbuilds
# php-cgi SAPI
%global with_cgi 0%{?_with_cgi:1}
%global with_fpm 0%{?_with_fpm:1}
%global with_test 0%{?_with_test:1}

# we can not provide devel package without CLI (due to phpize)
%if %{with_devel}
%global with_cli 1
%endif

%global _missing_build_ids_terminate_build 0
%global with_relocation 0%{?_with_relocation:1}

%if %{with_relocation}
%global program_suffix      85
%global main_name           php85
%global fpm_name            php85-fpm
%global php_sysconfdir      %{_sysconfdir}/php85
%global php_datadir         %{_datadir}/php85
%global pear_datadir        %{php_datadir}/pear
%global php_docdir          %{_docdir}/php85
%global tests_datadir       %{php_datadir}/tests
# configured by relocation patch (in other words - hardcoded)
%global fpm_config_name     php85-fpm.conf
%global fpm_config_d        %{php_sysconfdir}/php%{program_suffix}-fpm.d
%global bin_phar            phar%{program_suffix}
%global bin_cli             php%{program_suffix}
%global bin_cgi             php%{program_suffix}-cgi
%global bin_phpize          phpize%{program_suffix}
%global bin_phpdbg          phpdbg%{program_suffix}
%global bin_fpm             php%{program_suffix}-fpm
%global bin_php_config      php%{program_suffix}-config
%global php_includedir      %{_includedir}/php85
%else
%global main_name           php
%global fpm_name            php-fpm
%global php_sysconfdir      %{_sysconfdir}
%global php_datadir         %{_datadir}/php
%global pear_datadir        %{_datadir}/pear
%global php_docdir          %{_docdir}
%global tests_datadir       %{_datadir}/tests
%global fpm_config_name     php-fpm.conf
%global fpm_config_d        %{php_sysconfdir}/php-fpm.d
%global bin_phar            phar
%global bin_cli             php
%global bin_cgi             php-cgi
%global bin_phpize          phpize
%global bin_phpdbg          phpdbg
%global bin_fpm             php-fpm
%global bin_php_config      php-config
%global php_includedir      %{_includedir}/php
%endif

%global php_main            %{main_name}
%global php_common          %{php_main}-common
%global php_cli             %{php_main}-cli
%global php_cgi             %{php_main}-cgi
%global php_xml             %{php_main}-xml
%global php_bcmath          %{php_main}-bcmath
%global php_mysql           %{php_main}-mysql
%global php_mysqlnd         %{php_main}-mysqlnd
%global php_libdir          %{_libdir}/%{main_name}
%global fpm_rundir          %{_rundir}/%{fpm_name}
%global php_sharedstatedir  %{_sharedstatedir}/%{main_name}
%global fpm_sharedstatedir  %{_sharedstatedir}/%{fpm_name}
%global fpm_logdir          %{_localstatedir}/log/%{fpm_name}
%global fpm_config          %{php_sysconfdir}/%{fpm_config_name}
%global fpm_datadir         %{php_datadir}/fpm
%global fpm_service         %{fpm_name}
%global fpm_service_d       %{fpm_service}.service.d
%global fpm_unit            %{fpm_service}.service
%global fpm_logrotate       %{fpm_service}

%global apiver      20250925
%global zendver     20250925
%global pdover      20240423
# Extension version
%global fileinfover 1.0.5
%global zipver      1.22.8

# we don't want -z defs linker flag
%undefine _strict_symbol_defs_build

# Adds -z now to the linker flags
%global _hardened_build 1

# Use the arch-specific mysql_config binary to avoid mismatch with the
# arch detection heuristic used by bindir/mysql_config.
%global mysql_config %{_libdir}/mysql/mysql_config

%global mysql_sock %(mysql_config --socket 2>/dev/null || echo /var/lib/mysql/mysql.sock)

%global isasuffix -%{__isa_bits}

%global  _nginx_home    %{_localstatedir}/lib/nginx
# needed at srpm build time, when httpd-devel not yet installed
%{!?_httpd_mmn:         %{expand: %%global _httpd_mmn        %%(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}}

%{!?_httpd_apxs: %global _httpd_apxs %{_sbindir}/apxs}
%{!?_httpd_confdir: %global _httpd_confdir %{_sysconfdir}/httpd/conf.d}
%{!?_httpd_moddir: %global _httpd_moddir %{_libdir}/httpd/modules}

%bcond_without         dtrace
%bcond_without         zip

%global rpmrel 2
%global baserel %{rpmrel}%{?dist}

# liburiparser version 1.0.0 required
%global liburiparser_minver 1.0.0
%global liburiparser_bunver 1.0.2
%if 0%{?fedora} || 0%{?rhel} >= 11
# use system liburiparser when available
%bcond_without       liburiparser
%else
# use bundled library instead for now
%bcond_with          liburiparser
%endif

%global upver        8.5.7

Summary: PHP scripting language for creating dynamic web sites
Name: %{php_main}
Version: %{upver}
Release: %{rpmrel}%{?dist}

# All files licensed under PHP version 3.01, except
# Zend is licensed under Zend
# TSRM is licensed under BSD
# main/snprintf.c, main/spprintf.c and main/rfc1867.c are ASL 1.0
# ext/date/lib is MIT
# Zend/zend_sort is NCSA
# Zend/asm is Boost
# lexbor is Apache-2.0
License: PHP-3.01 AND Zend-2.0 AND BSD-2-Clause AND MIT AND Apache-1.0 AND Apache-2.0 AND NCSA AND BSL-1.0
URL: http://www.php.net/

Source0: https://www.php.net/distributions/php-%{version}.tar.xz
Source1: php.conf
Source2: php.ini
Source3: macros.php
Source4: php-fpm.conf
Source5: php-fpm-www.conf
Source6: php-fpm.service
Source7: php-fpm.logrotate
Source9: php.modconf
Source12: php-fpm.wants
Source13: nginx-fpm.conf
Source14: nginx-php.conf
Source15: php.tmpfiles
Source16: php-cgi-fcgi.ini

# See https://secure.php.net/gpg-keys.php
Source20: https://www.php.net/distributions/php-keyring.gpg
Source21: https://www.php.net/distributions/php-%{version}.tar.xz.asc

# Configuration files for some extensions
Source50: 10-opcache.ini
Source51: opcache-default.blacklist
Source53: 20-ffi.ini

# relocation resources
Source101: php85-php.conf
Source103: php85-macros.php
Source104: php85-php-fpm.conf
Source105: php85-php-fpm-www.conf
Source106: php85-php-fpm.service
Source107: php85-php-fpm.logrotate
Source112: php85-php-fpm.wants
Source113: php85-nginx-fpm.conf
Source114: php85-nginx-php.conf
Source115: php85-php.tmpfiles
Source150: php85-10-opcache.ini
Source153: php85-20-ffi.ini

# Build fixes
Patch1: php-8.4.0-httpd.patch
Patch5: php-8.5.0-includedir.patch
Patch8: php-8.4.0-libdb.patch

# Functional changes
# Use system nikic/php-parser
Patch41: php-8.5.0-parser.patch
# use system tzdata
Patch42: php-8.5.0-systzdata-v24.patch
# See http://bugs.php.net/53436
# + display PHP version backported from 8.4
Patch43: php-8.4.0-phpize.patch
# Use -lldap_r for OpenLDAP
Patch45: php-8.5.0-ldap_r.patch
# drop "Configure command" from phpinfo output
# and only use gcc (instead of full version)
Patch47: php-8.4.0-phpinfo.patch
# Always warn about missing curve_name
# Both Fedora and RHEL do not support arbitrary EC parameters
Patch48: php-8.5.0-openssl-ec-param.patch

Patch60: php-5.6.31-no-scan-dir-override.patch

# Upstream fixes (100+)

# Security fixes (200+)

# Fixes for tests (300+)
# Factory is droped from system tzdata
Patch300: php-7.4.0-datetests.patch

# relocation (400+)
Patch405: php85-php-8.5.0-includedir.patch
Patch409: php-7.0.8-relocation.patch

BuildRequires: autoconf >= 2.64
BuildRequires: bison
BuildRequires: bzip2-devel
BuildRequires: flex
BuildRequires: gcc-c++
BuildRequires: gdbm-devel
BuildRequires: httpd-devel >= 2.4
BuildRequires: libacl-devel
BuildRequires: libdb-devel
BuildRequires: libstdc++-devel
BuildRequires: libtool >= 1.4.3
BuildRequires: libtool-ltdl-devel
BuildRequires: make
%if %{with_fpm}
# to ensure we are using nginx with filesystem feature (see #1142298)
BuildRequires: nginx-filesystem
%endif
BuildRequires: openssl-devel >= 1.0.2
BuildRequires: perl
BuildRequires: pkgconfig(freetype2)
BuildRequires: pkgconfig(icu-i18n) >= 50.1
BuildRequires: pkgconfig(icu-io)   >= 50.1
BuildRequires: pkgconfig(icu-uc)   >= 50.1
BuildRequires: pkgconfig(libcurl) >= 7.29.0
BuildRequires: pkgconfig(libjpeg)
BuildRequires: pkgconfig(libpcre2-8) >= 10.30
BuildRequires: pkgconfig(capstone) >= 3.0
BuildRequires: pkgconfig(libpng)
BuildRequires: pkgconfig(libwebp)
BuildRequires: pkgconfig(libxcrypt)
BuildRequires: libxcrypt-devel
BuildRequires: pkgconfig(libxml-2.0)
BuildRequires: pkgconfig(oniguruma) >= 6.8
BuildRequires: pkgconfig(sqlite3) >= 3.7.4
BuildRequires: pkgconfig(zlib) >= 1.2.0.4
BuildRequires: smtpdaemon
%if %{with dtrace}
BuildRequires: systemtap-sdt-devel
%if 0%{?fedora} >= 41 || 0%{?rhel} >= 10
BuildRequires: systemtap-sdt-dtrace
%endif
%endif
%if %{with liburiparser}
BuildRequires: pkgconfig(liburiparser) >= %{liburiparser_minver}
%else
Provides:      bundled(liburiparser) = %{liburiparser_bunver}
%endif
BuildRequires: unixODBC-devel
# used for tests
BuildRequires: %{_bindir}/ps
BuildRequires: tzdata

Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
Requires: httpd-mmn = %{_httpd_mmn}
# to ensure we are using httpd with filesystem feature (see #1081453)
Requires: httpd-filesystem >= 2.4
Requires: libcurl

Requires(pre): httpd

# Don't provides extensions, which are not shared library, as .so
%global __provides_exclude_from %{?__provides_exclude_from:%__provides_exclude_from|}%{php_libdir}/modules/.*\\.so$

# php engine for Apache httpd webserver
Provides: php(httpd)
Provides: mod_php = %{version}-%{release}

%description
PHP is an HTML-embedded scripting language. PHP attempts to make it
easy for developers to write dynamically generated web pages. PHP also
offers built-in database integration for several commercial and
non-commercial database management systems, so writing a
database-enabled webpage with PHP is fairly simple. The most common
use of PHP coding is probably as a replacement for CGI scripts.

The %{name} package contai1.22.8ns the module (often referred to as mod_php)
which adds support for the PHP language to Apache HTTP Server.

%package common
Summary: Common files for PHP
# All files licensed under PHP version 3.01, except
# fileinfo is licensed under PHP version 3.0
# regex, libmagic are licensed under BSD
# libmbfl is licensed under LGPLv2
# ucgendat is licensed under OpenLDAP
License: PHP-3.01 AND BSD-2-Clause AND LGPL-2.1-only AND OLDAP-2.8
Requires: tzdata
# ABI/API check - Arch specific
Provides: php(api) = %{apiver}%{isasuffix}
Provides: php(zend-abi) = %{zendver}%{isasuffix}
Provides: php(language) = %{version}, php(language)%{?_isa} = %{version}
# Provides for all builtin/shared modules:
# Bzip2 support in PHP is not enabled by default. You will need to use the --with-bz2
Provides: php-bz2, php-bz2%{?_isa}
# To get these functions to work, you have to compile PHP with --enable-calendar
Provides: php-calendar, php-calendar%{?_isa}
Provides: php-core = %{version}, php-core%{?_isa} = %{version}
# Beginning with PHP 4.2.0 these functions are enabled by default
Provides: php-ctype, php-ctype%{?_isa}
# To use PHP's cURL support you must also compile PHP --with-curl
Provides: php-curl, php-curl%{?_isa}
Provides: php_database
# part of the PHP core
Provides: php-date, php-date%{?_isa}
Provides: bundled(timelib)
# using the --enable-dba configuration option you can enable PHP for basic support of dbm-style databases
# To enable support for gdbm add --with-gdbm
# To enable support for Oracle Berkeley DB 4 or 5 add --with-db4
Provides: php-dba, php-dba%{?_isa}
# php-ereg DEPRECATED in PHP 5.3.0, and REMOVED in PHP 7.0.0 (no --with-regex flag anymore)
# To enable exif-support configure PHP with --enable-exif
Provides: php-exif, php-exif%{?_isa}
# This extension is enabled by default as of PHP 5.3.0
Provides: php-fileinfo, php-fileinfo%{?_isa}
# the filter extension is enabled by default as of PHP 5.2.0
Provides: php-filter, php-filter%{?_isa}
# to use FTP functions with your PHP configuration, you should add the --enable-ftp
Provides: php-ftp, php-ftp%{?_isa}
# To enable GD-support configure PHP --with-gd
Provides: php-gd, php-gd%{?_isa}
Provides: bundled(gd) = 2.0.35
# To include GNU gettext support in your PHP build you must add the option --with-gettext
Provides: php-gettext, php-gettext%{?_isa}
# As of PHP 5.1.2, the Hash extension is bundled and compiled into PHP by default
Provides: php-hash, php-hash%{?_isa}
Provides: php-lexbor, php-lexbor%{?_isa}
# See ext/lexbor/patches/README.md
%global lexborver 2.7.0
Provides: bundled(lexbor) = %{lexborver}
# You need to compile PHP with the --with-mhash parameter to enable this extension
Provides: php-mhash, php-mhash%{?_isa}
# This extension is enabled by default
Provides: php-iconv, php-iconv%{?_isa}
# extension may be installed using the bundled version as of PHP 5.3.0, --enable-intl will enable the bundled version
Provides: php-intl, php-intl%{?_isa}
# As of PHP 5.2.0, the JSON extension is bundled and compiled into PHP by default
Provides: php-json, php-json%{?_isa}
Provides: bundled(libmagic) = 5.43
Provides: bundled(libmbfl) = 1.3.2
# The libxml extension is enabled by default
Provides: php-libxml, php-libxml%{?_isa}
# mbstring is a non-default extension. --enable-mbstring : Enable mbstring functions
Provides: php-mbstring, php-mbstring%{?_isa}
# mcrypt extension has been deprecated as of PHP 7.1.0 and moved to PECL as of PHP 7.2.0
Provides: php-mysqli%{?_isa} = %{version}-%{baserel}
Provides: php-mysqli = %{version}-%{baserel}
# mysql extension was DEPRECATED in PHP 5.5.0, and it was removed in PHP 7.0.0
# As of 5.4.0 The MySQL Native Driver is now the default for all MySQL extensions
Provides: php-mysqlnd = %{version}-%{baserel}
Provides: php-mysqlnd%{?_isa} = %{version}-%{baserel}
Provides: php-opcache = %{version}, php-opcache%{?_isa} = %{version}
# To use PHP's OpenSSL support you must also compile PHP --with-openssl
Provides: php-openssl, php-openssl%{?_isa}
# core PHP extension, so it is always enabled
Provides: php-pcre, php-pcre%{?_isa}
Provides: php-random, php-random%{?_isa}
Provides: php-pdo = %{version}-%{baserel}
Provides: php-pdo%{?_isa} = %{version}-%{baserel}
Provides: php-pdo-abi  = %{pdover}
Provides: php(pdo-abi) = %{pdover}
Provides: php-pdo-abi  = %{pdover}%{isasuffix}
Provides: php(pdo-abi) = %{pdover}%{isasuffix}
Provides: php-pdo_mysql, php-pdo_mysql%{?_isa}
# PDO and the PDO_SQLITE driver is enabled by default as of PHP 5.1.0
Provides: php-pdo_sqlite, php-pdo_sqlite%{?_isa}
# The Phar extension is built into PHP as of PHP version 5.3.0
Provides: php-phar, php-phar%{?_isa}
# they are part of the PHP core
Provides: php-reflection, php-reflection%{?_isa}
# Session support is enabled in PHP by default
Provides: php-session, php-session%{?_isa}
# enable SOAP support, configure PHP with --enable-soap
Provides: php-soap = %{version}-%{baserel}
Provides: php-soap%{?_isa} = %{version}-%{baserel}
# As of PHP 5.3.0 this extension can no longer be disabled and is therefore always available
Provides: php-spl, php-spl%{?_isa}
# The SQLite3 extension is enabled by default as of PHP 5.3.0
Provides: php-sqlite3, php-sqlite3%{?_isa}
Provides: php-standard = %{version}, php-standard%{?_isa} = %{version}
# these functions are enabled by default
Provides: php-tokenizer, php-tokenizer%{?_isa}
%if %{with zip}
# compile PHP with zip support by using the --with-zip
Provides: php-zip, php-zip%{?_isa}
Provides:  php-pecl(zip)         = %{zipver}
Provides:  php-pecl(zip)%{?_isa} = %{zipver}
Provides:  php-pecl-zip          = %{zipver}
Provides:  php-pecl-zip%{?_isa}  = %{zipver}
%endif
# Zlib support in PHP is not enabled by default. You will need to configure PHP --with-zlib
Provides: php-zlib, php-zlib%{?_isa}
Provides:  php-pecl-Fileinfo = %{fileinfover}, php-pecl-Fileinfo%{?_isa} = %{fileinfover}
Provides:  php-pecl(Fileinfo) = %{fileinfover}, php-pecl(Fileinfo)%{?_isa} = %{fileinfover}
%if ! %{with_relocation}
Obsoletes: php-dba < %{version}-%{baserel}
Obsoletes: php-gd < %{version}-%{baserel}
Obsoletes: php-intl  < %{version}-%{baserel}
Obsoletes: php-mbstring < %{version}-%{baserel}
Obsoletes: php-pdo < %{version}-%{baserel}
Obsoletes: php-soap < %{version}-%{baserel}
Obsoletes: php-xmlrpc < %{version}-%{baserel}
%endif
%if 0%{?rhel} >= 7
Requires(pre): httpd-filesystem
Requires: httpd-filesystem
%endif

%description common
The %{php_common} package contains files used by both the php
package and the %{php_cli} package.

%if %{with_cli}
%package cli

Summary: Command-line interface for PHP
# sapi/cli/ps_title.c is PostgreSQL
License: PHP-3.01 AND Zend-2.0 AND BSD-2-Clause AND MIT AND Apache-1.0 AND Apache-2.0 AND NCSA AND PostgreSQL
BuildRequires: pkgconfig(libedit)
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
Provides: %{php_cli}%{?_isa} = %{version}-%{baserel}
Provides: php-pcntl, php-pcntl%{?_isa}
Provides: php-readline, php-readline%{?_isa}

%description cli
The %{php_cli} package contains the command-line interface
executing PHP scripts, /usr/bin/php.
%endif

%if %{with_cgi}
%package cgi

Summary: CGI interface for PHP
# for monolithic config use we need ensure that all extensions are installed
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}

%description cgi
The php-cgi package contains the CGI interface executing
PHP scripts, /usr/bin/php-cgi
%endif

%if %{with_fpm}
%package fpm

Summary: PHP FastCGI Process Manager
BuildRequires: libacl-devel
BuildRequires: nginx-filesystem
BuildRequires: pkgconfig(libsystemd) >= 209
BuildRequires: pkgconfig(libselinux)
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
# for /etc/nginx ownership
Requires(pre): nginx-filesystem
Requires: nginx-filesystem

%description fpm
PHP-FPM (FastCGI Process Manager) is an alternative PHP FastCGI
implementation with some additional features useful for sites of
any size, especially busier sites.
%endif

%if %{with_devel}
%package devel
Summary: Files needed for building PHP extensions
Requires: %{php_cli}%{?_isa} = %{version}-%{baserel}
Requires: automake
Requires: autoconf
# see "php-config --libs"
Requires: krb5-devel%{?_isa}
Requires: libxml2-devel%{?_isa}
Requires: make
Requires: openssl-devel%{?_isa} >= 1.0.2
Requires: pcre2-devel%{?_isa}
Requires: zlib-devel%{?_isa}
Recommends: php-nikic-php-parser5 >= 5.6.1

%description devel
The php-devel package contains the files needed for building PHP
extensions. If you need to compile your own PHP extensions, you will
need to install this package.
%endif

%if %{with_xml}
%package xml
Summary: A module for PHP applications which use XML

# All files licensed under PHP version 3.01, except
License:  PHP-3.01
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
# This extension is enabled by default
Provides: php-dom, php-dom%{?_isa}
Provides: php-domxml, php-domxml%{?_isa}
# This extension is enabled by default.
Provides: php-simplexml, php-simplexml%{?_isa}
# enabled by default as of PHP 5.1.2
Provides: php-xmlreader, php-xmlreader%{?_isa}
# This extension is enabled by default.
Provides: php-xmlwriter, php-xmlwriter%{?_isa}
# PHP 5 includes the XSL extension by default and can be enabled by adding the argument --with-xsl
Provides: php-xsl, php-xsl%{?_isa}
BuildRequires: pkgconfig(libxslt)  >= 1.1
BuildRequires: pkgconfig(libexslt)
%global with_modules 1

%description xml
The php-xml package contains dynamic shared objects which add support
to PHP for manipulating XML documents using the DOM tree,
and performing XSL transformations on XML documents.
%endif

%if %{with_pgsql}
%package pgsql
Summary: A PostgreSQL database module for PHP

# All files licensed under PHP version 3.01
License:  PHP-3.01
BuildRequires: postgresql-devel
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
%global with_modules 1

%description pgsql
The php-pgsql package add PostgreSQL database support to PHP.
PostgreSQL is an object-relational database management
system that supports almost all SQL constructs. PHP is an
HTML-embedded scripting language. If you need back-end support for
PostgreSQL, you should install this package in addition to the main
php package.
%endif

%if %{with_odbc}
%package odbc
Summary: A module for PHP applications that use ODBC databases

# All files licensed under PHP version 3.01, except
# pdo_odbc is licensed under PHP version 3.0
License:  PHP-3.01
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
BuildRequires: unixODBC-devel
%global with_modules 1

%description odbc
The php-odbc package contains a dynamic shared object that will add
database support through ODBC to PHP. ODBC is an open specification
which provides a consistent API for developers to use for accessing
data sources (which are often, but not always, databases). PHP is an
HTML-embeddable scripting language. If you need ODBC support for PHP
applications, you will need to install this package and the php
package.
%endif

%if %{with_bcmath}
%package bcmath
Summary: A module for PHP applications for using the bcmath library

# All files licensed under PHP version 3.01, except
# libbcmath is licensed under LGPLv2+
License:  PHP-3.01 AND LGPL-2.1-or-later
# only available if PHP was configured with --enable-bcmath
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
%global with_modules 1

%description bcmath
The php-bcmath package contains a dynamic shared object that will add
support for using the bcmath library to PHP.
%endif

%if %{with_ldap}
%package ldap
Summary: A module for PHP applications that use LDAP

# All files licensed under PHP version 3.01
License:  PHP-3.01
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
BuildRequires: pkgconfig(libsasl2)
BuildRequires: openldap-devel
%global with_modules 1

%description ldap
The php-ldap adds Lightweight Directory Access Protocol (LDAP)
support to PHP. LDAP is a set of protocols for accessing directory
services over the Internet. PHP is an HTML-embedded scripting
language.
%endif

%if %{with_posix}
%package process
Summary: Modules for PHP script using system process interfaces

# All files licensed under PHP version 3.01
License:  PHP-3.01
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
Provides: php-posix, php-posix%{?_isa}
Provides: php-shmop, php-shmop%{?_isa}
Provides: php-sysvsem, php-sysvsem%{?_isa}
Provides: php-sysvshm, php-sysvshm%{?_isa}
Provides: php-sysvmsg, php-sysvmsg%{?_isa}
%global with_modules 1

%description process
The php-process package contains dynamic shared objects which add
support to PHP using system interfaces for inter-process
communication.
%endif

%if %{with_sodium}
%package sodium
Summary: Wrapper for the Sodium cryptographic library
# All files licensed under PHP version 3.0.1
License:  PHP-3.01
BuildRequires:  pkgconfig(libsodium) >= 1.0.9

Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
Obsoletes: php-pecl-libsodium2 < 3
Provides:  php-pecl(libsodium)         = %{version}
Provides:  php-pecl(libsodium)%{?_isa} = %{version}
%global with_modules 1

%description sodium
The php-sodium package provides a simple,
low-level PHP extension for the libsodium cryptographic library.
%endif

%if %{with_ffi}
%package ffi
Summary: Foreign Function Interface
# All files licensed under PHP version 3.0.1
License:  PHP-3.01
BuildRequires:  pkgconfig(libffi)
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
%global with_modules 1

%description ffi
FFI is one of the features that made Python and LuaJIT very useful for fast
prototyping. It allows calling C functions and using C data types from pure
scripting language and therefore develop “system code” more productively.

For PHP, FFI opens a way to write PHP extensions and bindings to C libraries
in pure PHP.
%endif

%if %{with_tidy}
%package tidy
Summary: Standard PHP module provides tidy library support
# All files licensed under PHP version 3.01
License:  PHP-3.01
BuildRequires: libtidy-devel
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
%global with_modules 1

%description tidy
The php-tidy package contains a dynamic shared object that will add
support for using the tidy library to PHP.
%endif

%if %{with_sockets}
%package sockets
Summary: Standard PHP module provides BSD sockets support
# All files licensed under PHP version 3.01
License:  PHP-3.01
Requires: %{php_common}%{?_isa} = %{version}-%{baserel}
%global with_modules 1

%description sockets
The socket extension implements a low-level interface to the socket
communication functions based on the popular BSD sockets, providing the
possibility to act as a socket server as well as a client.
%endif

%prep
%if %{with dtrace}
: Enable Dtrace build
%endif

# CentOS 7: gpgv: Can't check signature: Invalid public key algorithm
%if 0%{?fedora} || 0%{?rhel} >= 8
%{?gpgverify:%{gpgverify} --keyring='%{SOURCE20}' --signature='%{SOURCE21}' --data='%{SOURCE0}'}
%endif

%setup -q -n php-%{version}

%patch -P1 -p1 -b .mpmcheck

%if %{with_relocation}
%patch -P405 -p1
%else
%patch -P5 -p1 -b .includedir
%endif

%patch -P8 -p1 -b .libdb

%if %{with_relocation}
%patch -P409 -p1
%endif

%patch -P41 -p1 -b .syslib
%patch -P42 -p1 -b .systzdata
%patch -P43 -p1 -b .headers
%patch -P45 -p1 -b .ldap_r
%patch -P47 -p1 -b .phpinfo
%patch -P48 -p1 -b .ec-param

%patch -P60 -p1

# upstream patches

# security patches

# Fixes for tests
%patch -P300 -p1 -b .datetests

# Prevent %%doc confusion over LICENSE files
cp Zend/LICENSE ZEND_LICENSE
cp TSRM/LICENSE TSRM_LICENSE
cp Zend/asm/LICENSE BOOST_LICENSE
cp sapi/fpm/LICENSE fpm_LICENSE
cp ext/mbstring/libmbfl/LICENSE libmbfl_LICENSE
cp ext/fileinfo/libmagic/LICENSE libmagic_LICENSE
cp ext/bcmath/libbcmath/LICENSE libbcmath_LICENSE
cp ext/date/lib/LICENSE.rst timelib_LICENSE
cp ext/lexbor/LICENSE lexbor_LICENSE

# Multiple builds for multiple SAPIs
mkdir build-apache
%if %{with_cli}
mkdir build-cli
%endif
%if %{with_cgi}
mkdir build-cgi
%endif
%if %{with_fpm}
mkdir build-fpm
%endif

# ----- Manage known as failed test -------
# affected by systzdata patch
rm ext/date/tests/timezone_location_get.phpt
rm ext/date/tests/timezone_version_get.phpt
rm ext/date/tests/timezone_version_get_basic1.phpt
# fails sometime
rm -f ext/sockets/tests/mcast_ipv?_recv.phpt
# Both Fedora and RHEL do not support arbitrary EC parameters
# https://bugzilla.redhat.com/2223953
rm ext/openssl/tests/ecc_custom_params.phpt
# Failing when build with PHP installed
rm ext/opcache/tests/zzz_basic_logging.phpt

# Safety check for API version change.
pver=$(sed -n '/#define PHP_VERSION /{s/.* "//;s/".*$//;p}' main/php_version.h)
if test "x${pver}" != "x%{version}"; then
   : Error: Upstream PHP version is now ${pver}, expecting %{version}.
   : Update the version macros and rebuild.
   exit 1
fi

vapi=`sed -n '/#define PHP_API_VERSION/{s/.* //;p}' main/php.h`
if test "x${vapi}" != "x%{apiver}"; then
   : Error: Upstream API version is now ${vapi}, expecting %{apiver}.
   : Update the apiver macro and rebuild.
   exit 1
fi

vzend=`sed -n '/#define ZEND_MODULE_API_NO/{s/^[^0-9]*//;p;}' Zend/zend_modules.h`
if test "x${vzend}" != "x%{zendver}"; then
   : Error: Upstream Zend ABI version is now ${vzend}, expecting %{zendver}.
   : Update the zendver macro and rebuild.
   exit 1
fi

# Safety check for PDO ABI version change
vpdo=`sed -n '/#define PDO_DRIVER_API/{s/.*[ 	]//;p}' ext/pdo/php_pdo_driver.h`
if test "x${vpdo}" != "x%{pdover}"; then
   : Error: Upstream PDO ABI version is now ${vpdo}, expecting %{pdover}.
   : Update the pdover macro and rebuild.
   exit 1
fi

ver=$(sed -n '/#define PHP_ZIP_VERSION /{s/.* "//;s/".*$//;p}' ext/zip/php_zip.h)
if test "$ver" != "%{zipver}"; then
   : Error: Upstream ZIP version is now ${ver}, expecting %{zipver}.
   : Update the %{zipver} macro and rebuild.
   exit 1
fi

vlexbor=`sed -n '/Lexbor version/{s/.* is //;s/\.$//;p}' ext/lexbor/patches/README.md`
if test "x${vlexbor}" != "x%{lexborver}"; then
   : Error: Upstream Lexbor version is now ${vlexbor}, expecting %{lexborver}.
   : Update the lexborver macro and rebuild.
   exit 1
fi

vurimaj=$(sed  -n '/define URI_VER_MAJ/{s/.* //;s/\.$//;p}' ext/uri/uriparser/include/uriparser/UriBase.h)
vurimin=$(sed  -n '/define URI_VER_MIN/{s/.* //;s/\.$//;p}' ext/uri/uriparser/include/uriparser/UriBase.h)
vurirel=$(sed  -n '/define URI_VER_REL/{s/.* //;s/\.$//;p}' ext/uri/uriparser/include/uriparser/UriBase.h)
if test "x${vurimaj}.${vurimin}.${vurirel}" != "x%{liburiparser_bunver}"; then
   : Error: Upstream uriparser version is now ${vurimaj}.${vurimin}.${vurirel}, expecting %{liburiparser_bunver}.
   : Update the liburiparser_bunver macro and rebuild.
   exit 1
fi

# https://bugs.php.net/63362 - Not needed but installed headers.
# Drop some Windows specific headers to avoid installation,
# before build to ensure they are really not needed.
rm -f TSRM/tsrm_win32.h \
      TSRM/tsrm_config.w32.h \
      Zend/zend_config.w32.h \
      ext/mysqlnd/config-win.h \
      ext/standard/winver.h \
      main/win32_internal_function_disabled.h \
      main/win95nt.h

# Fix some bogus permissions
find . -name \*.[ch] -exec chmod 644 {} \;
chmod 644 README.*

# Some extensions have their own configuration file
%if %{with_relocation}
cat %{SOURCE150} > 10-opcache.ini
%else
cat %{SOURCE50} > 10-opcache.ini
%endif

%if %{with_ffi}
%if %{with_relocation}
cat %{SOURCE153} > 20-ffi.ini
%else
cat %{SOURCE53} > 20-ffi.ini
%endif
%endif

%build
%if 0%{?rhel} >= 9
# Disable LTO
%define _lto_cflags %{nil}
%endif

# Set build date from https://reproducible-builds.org/specs/source-date-epoch/
export SOURCE_DATE_EPOCH=$(date +%s -r NEWS)
export PHP_UNAME=$(uname)
export PHP_BUILD_SYSTEM=$(cat /etc/redhat-release | sed -e 's/ Beta//')
%if 0%{?vendor:1}
export PHP_BUILD_PROVIDER="%{vendor}"
%endif
export PHP_BUILD_COMPILER="$(gcc --version | head -n1)"
export PHP_BUILD_ARCH="%{_arch}"

# Force use of system libtool:
libtoolize --force --copy
cat `aclocal --print-ac-dir`/{libtool,ltoptions,ltsugar,ltversion,lt~obsolete}.m4 >build/libtool.m4

# Regenerate configure scripts (patches change config.m4's)
touch configure.ac
./buildconf --force

CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -Wno-pointer-sign"
export CFLAGS

# Install extension modules in %%{php_libdir}/modules.
EXTENSION_DIR=%{php_libdir}/modules; export EXTENSION_DIR

# Set PEAR_INSTALLDIR to ensure that the hard-coded include_path
# includes the PEAR directory even though pear is packaged
# separately.
PEAR_INSTALLDIR=%{pear_datadir}; export PEAR_INSTALLDIR

# Shell function to configure and build a PHP tree.
build() {
# Old/recent bison version seems to produce a broken parser;
# upstream uses GNU Bison 2.3. Workaround:
mkdir Zend && cp ../Zend/zend_{language,ini}_{parser,scanner}.[ch] Zend

# Always static:
# date, filter, libxml, reflection, spl: not supported
# hash: for PHAR_SIG_SHA256 and PHAR_SIG_SHA512
# session: dep on hash, used by soap
# pcre: used by filter
# openssl: for PHAR_SIG_OPENSSL
# zlib: used by image

ln -sf ../configure
%configure \
    --enable-rtld-now \
    --cache-file=../config.cache \
    --disable-debug \
    --disable-phpdbg \
    --disable-rpath \
    --enable-calendar \
    --enable-dba --with-db4=%{_prefix} --with-gdbm \
    --enable-exif \
    --enable-ftp \
    --enable-gd \
    --enable-intl \
    --enable-mbstring \
    --enable-mbregex \
    --enable-pdo \
    --enable-soap \
    --libdir=%{php_libdir} \
%if %{with_relocation}
    --sysconfdir=%{php_sysconfdir} \
%endif
    --with-bz2 \
    --with-capstone \
    --with-config-file-path=%{php_sysconfdir} \
    --with-curl \
    --with-external-pcre \
    --with-external-libcrypt \
%if %{with liburiparser}
    --with-external-uriparser \
%endif
    --with-freetype=%{_prefix} \
    --with-gettext \
    --with-jpeg=%{_prefix} \
    --with-layout=GNU \
    --with-libdir=%{_lib} \
    --with-mhash \
    --with-mysql-sock=%{mysql_sock} \
    --with-mysqli=mysqlnd \
    --with-pdo-mysql=mysqlnd \
    --with-openssl \
    --with-openssl-argon2 \
    --without-password-argon2 \
    --with-pdo-odbc=unixODBC,%{_prefix} \
    --with-pic \
    --with-system-ciphers \
    --with-system-tzdata \
    --with-webp \
%if %{with zip}
    --with-zip \
%endif
    --with-zlib \
    --without-pear \
%if %{with dtrace}
    --enable-dtrace \
%endif
%if %{with_sodium}
    --with-sodium=shared \
%else
    --without-sodium \
%endif
    --enable-opcache-file \
%if %{with_xml}
    --enable-dom=shared \
    --enable-simplexml=shared \
    --enable-xmlreader=shared \
    --enable-xmlwriter=shared \
    --with-xsl=shared,%{_prefix} \
%endif
%if %{with_pgsql}
    --with-pdo-pgsql=shared,%{_prefix} \
    --with-pgsql=shared \
%endif
%if %{with_odbc}
    --with-unixODBC=shared,%{_prefix} \
%endif
%if %{with_bcmath}
    --enable-bcmath=shared \
%endif
%if %{with_ldap}
    --with-ldap=shared --with-ldap-sasl \
%endif
%if %{with_posix}
    --enable-sysvmsg=shared --enable-sysvshm=shared --enable-sysvsem=shared \
    --enable-shmop=shared \
    --enable-posix=shared \
%endif
%if %{with_ffi}
    --with-ffi=shared \
%endif
%if %{with_tidy}
    --with-tidy=shared,%{_prefix} \
%endif
%if %{with_sockets}
    --enable-sockets=shared \
%endif
    --without-readline \
    $*
if test $? != 0; then
  tail -500 config.log
  : configure failed
  exit 1
fi

make -s V=0 %{?_smp_mflags}
}

# Build /usr/bin/php-cgi with the CGI SAPI, and most shared extensions
%if %{with_cgi}
pushd build-cgi

build \
%if %{with_relocation}
      --program-suffix=%{program_suffix} \
%endif
      --disable-cli \
      --without-libedit \
      --with-config-file-scan-dir=%{php_sysconfdir}/php-cgi-fcgi.d
popd
%endif

without_shared="--disable-bcmath --disable-dom \
      --disable-posix --disable-shmop \
      --disable-simplexml \
      --disable-sysvmsg --disable-sysvsem --disable-sysvshm \
      --disable-xmlreader --disable-xmlwriter --without-ffi --without-ldap \
      --without-pdo-pgsql --without-pgsql \
      --without-sodium --without-tidy --disable-sockets \
      --without-unixODBC --without-xsl"

# Build Apache module, and the CLI SAPI, /usr/bin/php
pushd build-apache
build --with-apxs2=%{_httpd_apxs} --disable-cgi \
%if %{with_relocation}
    --program-suffix=%{program_suffix} \
%endif
%if %{with_cgi}
    ${without_shared} \
%endif
    --disable-cli \
    --with-config-file-scan-dir=%{php_sysconfdir}/php.d
popd

%if %{with_cli}
# Build CLI SAPI, /usr/bin/php
pushd build-cli
build --disable-cgi \
    --enable-pcntl \
    --with-libedit \
%if %{with_relocation}
    --program-suffix=%{program_suffix} \
%endif
    ${without_shared} \
    --with-config-file-scan-dir=%{php_sysconfdir}/php.d
popd
%endif

# Build php-fpm
%if %{with_fpm}
pushd build-fpm
build --enable-fpm \
%if %{with_relocation}
    --program-suffix=%{program_suffix} \
%endif
    --with-fpm-acl \
    --with-fpm-systemd \
    --with-fpm-selinux \
    --disable-cgi \
    --disable-cli \
    ${without_shared} \
    --with-config-file-scan-dir=%{php_sysconfdir}/php.d
popd
%endif

%check
%if %{with_test}
cd build-apache

# Run tests, using the CLI SAPI
export NO_INTERACTION=1 REPORT_EXIT_STATUS=1 MALLOC_CHECK_=2
export SKIP_ONLINE_TESTS=1
export SKIP_IO_CAPTURE_TESTS=1
unset TZ LANG LC_ALL
if ! make test TESTS=%{?_smp_mflags}; then
  set +x
  for f in $(find .. -name \*.diff -type f -print); do
    if ! grep -q XFAIL "${f/.diff/.phpt}"
    then
      echo "TEST FAILURE: $f --"
      cat "$f"
      echo -e "\n-- $f result ends."
    fi
  done
  set -x
  #exit 1
fi
unset NO_INTERACTION REPORT_EXIT_STATUS MALLOC_CHECK_
%endif

%install
# Install everything from the CGI SAPI build
%if %{with_cgi}
make -C build-cgi install-cgi  \
%if %{with_modules}
    install-modules \
%endif
    INSTALL_ROOT=$RPM_BUILD_ROOT
%else
%if %{with_modules}
make -C build-apache install-modules INSTALL_ROOT=$RPM_BUILD_ROOT
%endif
%endif

# all except install-sapi - use apxs for rpmbuild is failed (httpd.conf is missed)
make -C build-apache install-binaries \
    INSTALL_ROOT=$RPM_BUILD_ROOT

%if %{with_cli}
make -C build-cli install-cli \
%if %{with_devel}
    install-build install-headers \
%endif
    install-pharcmd \
    install-programs \
    INSTALL_ROOT=$RPM_BUILD_ROOT
%endif

# Install the php-fpm binary
%if %{with_fpm}
make -C build-fpm install-fpm \
    INSTALL_ROOT=$RPM_BUILD_ROOT
%endif

# Install the default configuration file
%if %{with_common}
install -m 755 -d $RPM_BUILD_ROOT%{php_sysconfdir}/
install -m 644 %{SOURCE2} $RPM_BUILD_ROOT%{php_sysconfdir}/php.ini

# For third-party packaging:
install -m 755 -d $RPM_BUILD_ROOT%{php_libdir}/pear \
%if %{with_ffi}
                  $RPM_BUILD_ROOT%{php_datadir}/preload
%else
                  $RPM_BUILD_ROOT%{php_datadir}
%endif
%endif

# Install tmpfiles.d file
%if %{with_relocation}
install -p -D -m 0644 %{SOURCE115} %{buildroot}%{_tmpfilesdir}/php%{program_suffix}.conf
%else
install -p -D -m 0644 %{SOURCE15} %{buildroot}%{_tmpfilesdir}/php.conf
%endif

# install the DSO
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_moddir}
install -m 755 build-apache/libs/libphp.so $RPM_BUILD_ROOT%{_httpd_moddir}

# Apache config fragment
install -m 755 -d $RPM_BUILD_ROOT%{_httpd_confdir}
# Due to posibility of use apache 2.2 and 2.4 we copy it locally
%if %{with_relocation}
cat %{SOURCE101} > httpd-php.conf
%else
cat %{SOURCE1} > httpd-php.conf
%endif
install -D -m 644 httpd-php.conf $RPM_BUILD_ROOT%{_httpd_confdir}/02-php.conf

# Dual config file with httpd >= 2.4 (fedora >= 18)
install -D -m 644 %{SOURCE9} $RPM_BUILD_ROOT%{_httpd_modconfdir}/20-php.conf

%if %{with_common}
install -m 755 -d $RPM_BUILD_ROOT%{php_sysconfdir}/php.d
install -m 755 -d $RPM_BUILD_ROOT%{php_sharedstatedir}
install -m 755 -d $RPM_BUILD_ROOT%{php_sharedstatedir}/peclxml
install -m 700 -d $RPM_BUILD_ROOT%{php_sharedstatedir}/session
install -m 700 -d $RPM_BUILD_ROOT%{php_sharedstatedir}/wsdlcache
install -m 700 -d $RPM_BUILD_ROOT%{php_sharedstatedir}/opcache
install -m 755 -d $RPM_BUILD_ROOT%{php_docdir}/pecl
install -m 755 -d $RPM_BUILD_ROOT%{tests_datadir}/pecl
install -m 755 -d $RPM_BUILD_ROOT%{php_sysconfdir}/php-cgi-fcgi.d
%endif

%if %{with_cgi}
# install config
sed "s,@LIBDIR@,%{_libdir},g" \
    < %{SOURCE16} > php-cgi-fcgi.ini
install -D -m 644 php-cgi-fcgi.ini \
           $RPM_BUILD_ROOT%{php_sysconfdir}/php-cgi-fcgi.ini
%endif

# PHP-FPM stuff
# Log
%if %{with_fpm}
install -m 700 -d $RPM_BUILD_ROOT%{fpm_sharedstatedir}/session
install -m 700 -d $RPM_BUILD_ROOT%{fpm_sharedstatedir}/wsdlcache
install -m 700 -d $RPM_BUILD_ROOT%{fpm_sharedstatedir}/opcache
install -m 755 -d $RPM_BUILD_ROOT%{fpm_logdir}
install -m 755 -d $RPM_BUILD_ROOT%{fpm_rundir}
# Config
install -m 755 -d $RPM_BUILD_ROOT%{fpm_config_d}
# LogRotate
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d
%if %{with_relocation}
install -m 644 %{SOURCE104} $RPM_BUILD_ROOT%{fpm_config}
install -m 644 %{SOURCE105} $RPM_BUILD_ROOT%{fpm_config_d}/www.conf
install -m 644 %{SOURCE107} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{fpm_logrotate}
# Nginx configuration
install -D -m 644 %{SOURCE113} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/%{fpm_name}.conf
install -D -m 644 %{SOURCE114} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/default.d/%{main_name}.conf
%else
install -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{fpm_config}
install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{fpm_config_d}/www.conf
install -m 644 %{SOURCE7} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/%{fpm_logrotate}
# Nginx configuration
install -D -m 644 %{SOURCE13} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/conf.d/%{fpm_name}.conf
install -D -m 644 %{SOURCE14} $RPM_BUILD_ROOT%{_sysconfdir}/nginx/default.d/%{main_name}.conf
%endif

mv $RPM_BUILD_ROOT%{fpm_config}.default .
mv $RPM_BUILD_ROOT%{fpm_config_d}/www.conf.default .

# install systemd unit files and scripts for handling server startup
install -m 755 -d $RPM_BUILD_ROOT%{_sysconfdir}/systemd/system/%{fpm_service_d}
install -m 755 -d $RPM_BUILD_ROOT%{_unitdir}
%if %{with_relocation}
install -m 644 %{SOURCE106} $RPM_BUILD_ROOT%{_unitdir}/%{fpm_unit}
install -D -m 644 %{SOURCE112} $RPM_BUILD_ROOT%{_unitdir}/httpd.service.d/%{fpm_service}.conf
install -D -m 644 %{SOURCE112} $RPM_BUILD_ROOT%{_unitdir}/nginx.service.d/%{fpm_service}.conf
%else
install -m 644 %{SOURCE6} $RPM_BUILD_ROOT%{_unitdir}/%{fpm_unit}
install -D -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_unitdir}/httpd.service.d/%{fpm_service}.conf
install -D -m 644 %{SOURCE12} $RPM_BUILD_ROOT%{_unitdir}/nginx.service.d/%{fpm_service}.conf
%endif
%endif

TESTCMD="$RPM_BUILD_ROOT%{_bindir}/%{bin_cli} --no-php-ini"
# Ensure all provided extensions are really there
for mod in core date filter hash json lexbor libxml openssl pcre random reflection session spl standard uri zlib
do
     $TESTCMD --modules | grep -qi $mod
done

TESTCMD="$TESTCMD --define extension_dir=$RPM_BUILD_ROOT%{php_libdir}/modules"

%if %{with_modules}
# Generate files lists and stub .ini files for each subpackage
for mod in \
%if %{with_bcmath}
    bcmath \
%endif
%if %{with_xml}
    dom simplexml xmlreader xmlwriter xsl \
%endif
    opcache \
%if %{with_pgsql}
    pgsql pdo_pgsql \
%endif
%if %{with_odbc}
    odbc \
%endif
%if %{with_ldap}
    ldap \
%endif
%if %{with_posix}
    posix shmop sysvshm sysvsem sysvmsg \
%endif
%if %{with_sodium}
    sodium \
%endif
%if %{with_ffi}
    ffi \
%endif
%if %{with_tidy}
    tidy \
%endif
%if %{with_sockets}
    sockets \
%endif
    ; do
    case $mod in
      opcache)
        # static extension
        ini=10-${mod}.ini;;
      xsl|dom|xmlreader|xmlwriter|simplexml)
        # Extensions with dependencies on 20-*
        TESTCMD="$TESTCMD --define extension=$mod"
        ini=30-${mod}.ini;;
      *)
        # Extensions with no dependency
        TESTCMD="$TESTCMD --define extension=$mod"
        ini=20-${mod}.ini;;
    esac

    $TESTCMD --modules | grep -qi $mod

    # some extensions have their own config file
    if [ -f ${ini} ]; then
      install -D -m 644 ${ini} $RPM_BUILD_ROOT%{php_sysconfdir}/php.d/${ini}
    else
      install -d -m 755 $RPM_BUILD_ROOT%{php_sysconfdir}/php.d
      cat > $RPM_BUILD_ROOT%{php_sysconfdir}/php.d/${ini} <<EOF
; Enable ${mod} extension module
extension=${mod}
EOF
    fi
%if %{with_cgi}
    install -d -m 755 $RPM_BUILD_ROOT%{php_sysconfdir}/php-cgi-fcgi.d
    cp -p $RPM_BUILD_ROOT%{php_sysconfdir}/{php.d,php-cgi-fcgi.d}/${ini}
    cat > files.${mod} <<EOF
%{php_libdir}/modules/${mod}.so
%config(noreplace) %{php_sysconfdir}/php.d/${ini}
%config(noreplace) %{php_sysconfdir}/php-cgi-fcgi.d/${ini}
EOF
%else
    cat > files.${mod} <<EOF
%{php_libdir}/modules/${mod}.so
%config(noreplace) %{php_sysconfdir}/php.d/${ini}
EOF
%endif
done
%endif

%if %{with_xml}
# The dom, xsl and xml* modules are all packaged in php-xml
cat files.dom files.xsl files.xml{reader,writer} \
    files.simplexml >> files.xml
%endif

%if %{with_posix}
# sysv* and posix in packaged in php-process
cat files.shmop files.sysv* files.posix > files.process
%endif

%if %{with_pgsql}
# postgres support as separate php-pgsql package
cat files.pdo_pgsql >> files.pgsql
%endif

# The default Zend OPcache blacklist file
rm files.opcache
install -m 644 %{SOURCE51} $RPM_BUILD_ROOT%{php_sysconfdir}/php.d/opcache-default.blacklist

%if %{with_devel}
%if %{with_relocation}
cat %{SOURCE103} > macros.php
%else
cat %{SOURCE3} > macros.php
%endif

# Install the macros file:
sed -i -e "s/@PHP_APIVER@/%{apiver}%{isasuffix}/" \
    -e "s/@PHP_ZENDVER@/%{zendver}%{isasuffix}/" \
    -e "s/@PHP_PDOVER@/%{pdover}%{isasuffix}/" \
    -e "s/@PHP_VERSION@/%{version}/" \
    -e "/zts/d" macros.php
mkdir -p $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d
install -m 644 -D macros.php \
           $RPM_BUILD_ROOT%{_rpmconfigdir}/macros.d/macros.%{php_main}
%endif

# Remove unpackaged files
rm -rf $RPM_BUILD_ROOT%{php_libdir}/modules/*.a \
       $RPM_BUILD_ROOT%{_bindir}/{phptar} \
       $RPM_BUILD_ROOT%{_datadir}/pear \
       $RPM_BUILD_ROOT%{_bindir}/zts-phar* \
       $RPM_BUILD_ROOT%{_mandir}/man1/zts-phar* \
       $RPM_BUILD_ROOT%{pear_datadir} \
       $RPM_BUILD_ROOT%{_libdir}/libphp.a \
       $RPM_BUILD_ROOT%{_libdir}/libphp.la

# Remove irrelevant docs
rm -f README.{Zeus,QNX,CVS-RULES}

%if %{with_fpm}
%pre fpm
getent group nginx >/dev/null || \
  groupadd -r nginx
getent passwd nginx >/dev/null || \
    useradd -r -d %{_nginx_home} -g nginx \
    -s /sbin/nologin -c "Nginx web server" nginx
exit 0

%post fpm
%systemd_post %{fpm_unit}

%preun fpm
%systemd_preun %{fpm_unit}

%postun fpm
%systemd_postun_with_restart %{fpm_unit}
%endif

%files
%{_httpd_moddir}/libphp.so
%config(noreplace) %{_httpd_confdir}/02-php.conf
%config(noreplace) %{_httpd_modconfdir}/20-php.conf

%if %{with_common}
%files common
%doc EXTENSIONS NEWS UPGRADING* README.REDIST.BINS *md docs
%license LICENSE TSRM_LICENSE ZEND_LICENSE BOOST_LICENSE
%license libmbfl_LICENSE
%license libmagic_LICENSE
%license timelib_LICENSE
%license lexbor_LICENSE
%doc php.ini-*
%config(noreplace) %{php_sysconfdir}/php.ini
%config(noreplace) %{_sysconfdir}/php.d/10-opcache.ini
%config(noreplace) %{_sysconfdir}/php.d/opcache-default.blacklist
%dir %{php_sysconfdir}/php.d
%dir %{php_sysconfdir}/php-cgi-fcgi.d
%dir %{php_libdir}
%dir %{php_libdir}/modules
%dir %{php_sharedstatedir}
%dir %{php_sharedstatedir}/peclxml
%dir %{php_datadir}
%dir %{php_docdir}/pecl
%dir %{tests_datadir}
%dir %{tests_datadir}/pecl
%attr(0770,root,apache) %dir %{php_sharedstatedir}/session
%attr(0770,root,apache) %dir %{php_sharedstatedir}/wsdlcache
%attr(0770,root,apache) %dir %{php_sharedstatedir}/opcache
%if %{with_relocation}
%{_tmpfilesdir}/php%{program_suffix}.conf
%else
%{_tmpfilesdir}/php.conf
%endif
%endif

%if %{with_cli}
%files cli
%{_bindir}/%{bin_cli}
%{_bindir}/%{bin_phar}.phar
%{_bindir}/%{bin_phar}
# provides phpize here (not in -devel) for pecl command
%{_bindir}/%{bin_phpize}
%{_mandir}/man1/%{bin_cli}.1*
%{_mandir}/man1/%{bin_phar}.1*
%{_mandir}/man1/%{bin_phar}.phar.1*
%{_mandir}/man1/%{bin_phpize}.1*
# move php-config here in case if devel package disabled
%if ! %{with_devel}
%exclude %{_bindir}/%{bin_php_config}
%exclude %{_mandir}/man1/%{bin_php_config}.1*
%endif
%endif

%if %{with_cgi}
%files cgi
%{_bindir}/%{bin_cgi}
%config(noreplace) %{php_sysconfdir}/php-cgi-fcgi.ini
%{_mandir}/man1/%{bin_cgi}.1*
%endif

%if %{with_fpm}
%files fpm
%doc %{fpm_config_name}.default www.conf.default
%doc fpm_LICENSE
%{_sbindir}/%{bin_fpm}
%attr(0770,root,nginx) %dir %{fpm_sharedstatedir}/session
%attr(0770,root,nginx) %dir %{fpm_sharedstatedir}/wsdlcache
%attr(0770,root,nginx) %dir %{fpm_sharedstatedir}/opcache
%config(noreplace) %{_sysconfdir}/nginx/conf.d/%{fpm_name}.conf
%config(noreplace) %{_sysconfdir}/nginx/default.d/%{main_name}.conf
%config(noreplace) %{fpm_config}
%config(noreplace) %{fpm_config_d}/www.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{fpm_logrotate}
%dir %{_sysconfdir}/systemd/system/%{fpm_service_d}
%{_unitdir}/%{fpm_unit}
%config(noreplace) %{_unitdir}/httpd.service.d/%{fpm_service}.conf
%config(noreplace) %{_unitdir}/nginx.service.d/%{fpm_service}.conf
%dir %{fpm_config_d}
# log owned by apache for log
%attr(770,nginx,root) %dir %{fpm_logdir}
%dir %ghost %{fpm_rundir}
%{_mandir}/man8/%{bin_fpm}.8*
%dir %{fpm_datadir}
%{fpm_datadir}/status.html
%endif

%if %{with_devel}
%files devel
%{_bindir}/%{bin_php_config}
%{php_includedir}
%{php_libdir}/build
%{_mandir}/man1/%{bin_php_config}.1*
%{_rpmconfigdir}/macros.d/macros.%{php_main}
%endif

%if %{with_xml}
%files xml -f files.xml
%endif

%if %{with_bcmath}
%files bcmath -f files.bcmath
%doc libbcmath_LICENSE
%endif

%if %{with_posix}
%files process -f files.process
%endif

%if %{with_pgsql}
%files pgsql -f files.pgsql
%endif

%if %{with_odbc}
%files odbc -f files.odbc
%endif

%if %{with_ldap}
%files ldap -f files.ldap
%endif

%if %{with_sodium}
%files sodium -f files.sodium
%endif

%if %{with_ffi}
%files ffi -f files.ffi
%dir %{php_datadir}/preload
%endif

%if %{with_tidy}
%files tidy -f files.tidy
%endif

%if %{with_sockets}
%files sockets -f files.sockets
%endif

%changelog
* Thu Jun  4 2026 Remi Collet <remi@remirepo.net> - 8.5.7-2
- use system liburiparser on RHEL-11
- bump ABI/API numbers to 20240925
- drop opcache subpackage, extension is build statically
- add lexbor and uri extension (always static)
- move /usr/share/fpm/status.html to /usr/share/php/fpm/status.html
- add tmpfiles.d configuration file

* Wed Jun  3 2026 Remi Collet <remi@remirepo.net> - 8.5.7-1
- Update to 8.5.7 - http://www.php.net/releases/8_5_7.php

* Wed Mar 11 2026 Remi Collet <remi@remirepo.net> - 8.4.19-1
- Update to 8.4.19 - http://www.php.net/releases/8_4_19.php

* Wed Jan 14 2026 Remi Collet <remi@remirepo.net> - 8.4.17-1
- Update to 8.4.17 - http://www.php.net/releases/8_4_17.php

* Wed Jul 30 2025 Remi Collet <remi@remirepo.net> - 8.4.11-1
- Update to 8.4.11 - http://www.php.net/releases/8_4_11.php

* Wed Jul  2 2025 Remi Collet <remi@remirepo.net> - 8.4.10-1
- Update to 8.4.10 - http://www.php.net/releases/8_4_10.php

* Tue Jul 30 2024 Remi Collet <remi@remirepo.net> - 8.3.10-1
- Update to 8.3.10 - http://www.php.net/releases/8_3_10.php

* Wed Apr 10 2024 Remi Collet <remi@remirepo.net> - 8.3.6-1
- Update to 8.3.6 - http://www.php.net/releases/8_3_6.php

* Thu Nov 30 2023 Remi Collet <remi@remirepo.net> - 8.3.0-2
- rebuild for libcapstone

* Wed Nov 22 2023 Remi Collet <remi@remirepo.net> - 8.3.0-1
- Update to 8.3.0 GA - http://www.php.net/releases/8_3_0.php
- tzdata is required
- add internal UTC if tzdata is missing
- bump to final API/ABI
- switch to nikic/php-parser version 5
- openssl: always warn about missing curve_name

* Tue Sep 26 2023 Remi Collet <remi@remirepo.net> - 8.2.11-1
- Update to 8.2.11 - http://www.php.net/releases/8_2_11.php

* Tue Sep 19 2023 Remi Collet <remi@remirepo.net> - 8.2.10-2
- require tzdata

* Tue Aug 29 2023 Remi Collet <remi@remirepo.net> - 8.2.10-1
- Update to 8.2.10 - http://www.php.net/releases/8_2_10.php

* Thu Aug  3 2023 Remi Collet <remi@remirepo.net> - 8.2.9-2
- Update to 8.2.9 - http://www.php.net/releases/8_2_9.php

* Wed Jul  5 2023 Remi Collet <remi@remirepo.net> - 8.2.8-2
- move httpd/nginx wants directive to config files in /etc

* Wed Jul  5 2023 Remi Collet <remi@remirepo.net> - 8.2.8-1
- Update to 8.2.8 - http://www.php.net/releases/8_2_8.php

* Wed Jun  7 2023 Remi Collet <remi@remirepo.net> - 8.2.7-2
- Update to 8.2.7 - http://www.php.net/releases/8_2_7.php

* Wed May 10 2023 Remi Collet <remi@remirepo.net> - 8.2.6-1
- Update to 8.2.6 - http://www.php.net/releases/8_2_6.php
- use SPDX license IDs

* Wed Apr 12 2023 Remi Collet <remi@remirepo.net> - 8.2.5-1
- Update to 8.2.5 - http://www.php.net/releases/8_2_5.php

* Wed Jan  4 2023 Remi Collet <remi@remirepo.net> - 8.2.1-1
- Update to 8.2.1 - http://www.php.net/releases/8_2_1.php

* Mon Dec 19 2022 Remi Collet <remi@remirepo.net> - 8.2.1~RC1-2
- php-fpm.conf: move include directive after [global] section
  following upstream example

* Mon Dec 19 2022 Alexander Ursu <alexander.ursu@gmail.com> - 8.2.0-1
- update to 8.2.0 GA

* Sat Dec 10 2022 Alexander Ursu <alexander.ursu@gmail.com> - 8.1.13-2
- Disable LTO for CentOS 9 Stream

* Tue Nov 22 2022 Remi Collet <remi@remirepo.net> - 8.1.13-1
- Update to 8.1.13 - http://www.php.net/releases/8_1_13.php

* Thu Sep  1 2022 Remi Collet <remi@remirepo.net> - 8.1.10-1
- Update to 8.1.10 - http://www.php.net/releases/8_1_10.php

* Wed Aug 17 2022 Remi Collet <remi@remirepo.net> - 8.1.10~RC1-1
- update to 8.1.10RC1

* Wed Jul  6 2022 Remi Collet <remi@remirepo.net> - 8.1.8-1
- Update to 8.1.8 - http://www.php.net/releases/8_1_8.php

* Wed May 11 2022 Remi Collet <remi@remirepo.net> - 8.1.6-1
- Update to 8.1.6 - http://www.php.net/releases/8_1_6.php

* Wed Feb 23 2022 Remi Collet <remi@remirepo.net> - 8.1.3-2
- retrieve tzdata version #2056611

* Wed Feb 16 2022 Remi Collet <remi@remirepo.net> - 8.1.3-1
- Update to 8.1.3 - http://www.php.net/releases/8_1_3.php

* Wed Dec 15 2021 Remi Collet <remi@remirepo.net> - 8.1.1-1
- Update to 8.1.1 - http://www.php.net/releases/8_1_1.php

* Wed Nov 24 2021 Remi Collet <remi@remirepo.net> - 8.1.0-1
- update to 8.1.0 GA
- bump API version

* Wed Nov 17 2021 Remi Collet <remi@remirepo.net> - 8.0.13-1
- Update to 8.0.13 - http://www.php.net/releases/8_0_13.php
- phar: switch to sha256 signature by default, backported from 8.1
- phar: implement openssl_256 and openssl_512 for signatures, backported from 8.1
- snmp: add sha256 / sha512 security protocol, backported from 8.1
- adapt systzdata patch for timelib 2020.03 (v20)

* Tue Oct 19 2021 Remi Collet <remi@remirepo.net> - 8.0.12-1
- Update to 8.0.12 - http://www.php.net/releases/8_0_12.php
- build using system libxcrypt

* Tue Jun 29 2021 Remi Collet <remi@remirepo.net> - 8.0.8-1
- Update to 8.0.8 - http://www.php.net/releases/8_0_8.php

* Wed Jun  2 2021 Remi Collet <remi@remirepo.net> - 8.0.7-1
- Update to 8.0.7 - http://www.php.net/releases/8_0_7.php
- fix snmp extension for net-snmp without DES

* Wed May  5 2021 Remi Collet <remi@remirepo.net> - 8.0.6-1
- Update to 8.0.6 - http://www.php.net/releases/8_0_6.php

* Tue Feb  2 2021 Remi Collet <remi@remirepo.net> - 8.0.2-1
- Update to 8.0.2 - http://www.php.net/releases/8_0_2.php

* Thu Jan 28 2021 Remi Collet <remi@remirepo.net> - 8.0.2~RC1-2
- add upstream patch for https://bugs.php.net/80682

* Wed Nov 25 2020 Remi Collet <remi@remirepo.net> - 8.0.0-1
- update to 8.0.0 GA

* Wed Sep 30 2020 Remi Collet <remi@remirepo.net> - 8.0.0~rc1-34
- update to 8.0.0rc1
- bump ABI/API versions

* Thu Sep 17 2020 Remi Collet <remi@remirepo.net> - 8.0.0~beta4-4
- drop mod_php for ZTS (have never be suported)
- use %%bcond_without for zip, dtrace
  so can be disabled during rebuild

* Fri Sep 11 2020 Remi Collet <remi@remirepo.net> - 8.0.0~beta3-1
- update to 8.0.0beta3
- bump ABI/API versions
- drop xmlrpc extension
- use system nikic/php-parser if available to generate
  C headers from PHP stub
- rename 15-php.conf to 20-php.conf to ensure load order

* Tue Sep  1 2020 Remi Collet <remi@remirepo.net> - 7.4.10-1
- Update to 7.4.10 - http://www.php.net/releases/7_4_10.php

* Tue Jul  7 2020 Remi Collet <remi@remirepo.net> - 7.4.8-1
- Update to 7.4.8 - http://www.php.net/releases/7_4_8.php
- display build system and provider in phpinfo (from 8.0)
- drop patch to fix PHP_UNAME

* Tue Jun  9 2020 Remi Collet <remi@remirepo.net> - 7.4.7-1
- Update to 7.4.7 - http://www.php.net/releases/7_4_7.php

* Mon May 25 2020 Alexander Ursu <alexander.ursu@gmail.com> - 7.4.6-4
- Added sockets extension as separate package

* Sun May 24 2020 Alexander Ursu <alexander.ursu@gmail.com> - 7.4.6-3
- separate CLI build from apache2handler. Enable pcntl for CLI

* Mon May 18 2020 Alexander Ursu <alexander.ursu@gmail.com> - 7.4.6-2
- enable tidy extension (shared)

* Tue May 12 2020 Remi Collet <remi@remirepo.net> - 7.4.6-1
- Update to 7.4.6 - http://www.php.net/releases/7_4_6.php

* Wed Dec 18 2019 Remi Collet <remi@remirepo.net> - 7.4.1-1
- Update to 7.4.1 - http://www.php.net/releases/7_4_1.php

* Mon Dec  2 2019 Alexander Ursu <alexander.ursu@gmail.com> - 7.4.0-2
- corrected relocated build's configuration files

* Wed Nov 27 2019 Remi Collet <remi@remirepo.net> - 7.4.0-1
- update to 7.4.0 GA

* Fri Nov 01 2019 Pete Walter <pwalter@fedoraproject.org> - 7.4.0~RC5-2
- Rebuild for ICU 65

* Tue Oct 29 2019 Remi Collet <remi@remirepo.net> - 7.4.0~RC5-1
- update to 7.4.0RC5
- set opcache.enable_cli in provided default configuration
- add /usr/share/php/preload as default ffi.preload configuration

* Tue Oct 15 2019 Remi Collet <remi@remirepo.net> - 7.4.0~RC4-1
- update to 7.4.0RC4

* Mon Oct  7 2019 Remi Collet <remi@remirepo.net> - 7.4.0~RC3-2
- ensure all shared extensions can be loaded
- add patch from https://github.com/php/php-src/pull/4794
  to ensure opcache is always linked with librt

* Tue Oct  1 2019 Remi Collet <remi@remirepo.net> - 7.4.0~RC3-1
- update to 7.4.0RC3
- bump API version to 20190902
- drop wddx, recode and interbase extensions
- add ffi extension
- drop dependency on libargon2, use libsodium implementation
- run test suite using 4 concurrent workers
- cleanup unused conditional
- add upstream patch to fix aarch64 build

* Wed Aug 28 2019 Remi Collet <remi@remirepo.net> - 7.3.9-1
- Update to 7.3.9 - http://www.php.net/releases/7_3_9.php

* Wed Jul  3 2019 Remi Collet <remi@remirepo.net> - 7.3.7-2
- Update to 7.3.7 - http://www.php.net/releases/7_3_7.php
- disable opcache.huge_code_pages in default configuration

* Wed May  1 2019 Remi Collet <remi@remirepo.net> - 7.3.5-1
- Update to 7.3.5 - http://www.php.net/releases/7_3_5.php

* Tue Apr  2 2019 Remi Collet <remi@remirepo.net> - 7.3.4-2
- Update to 7.3.4 - http://www.php.net/releases/7_3_4.php
- add upstream patches for failed tests
- add build dependency on ps command

* Thu Mar 28 2019 Alexander Ursu <alexander.ursu@gmail.com> - 7.3.3-2
- fixed ioncube package
- updated ioncube loader to version 10.3.2

* Wed Mar  6 2019 Remi Collet <remi@remirepo.net> - 7.3.3-1
- Update to 7.3.3 - http://www.php.net/releases/7_3_3.php
- add upstream patch for OpenSSL 1.1.1b
- adapt systzdata patch (v18)

* Tue Mar  5 2019 Alexander Ursu <alexander.ursu@gmail.com> - 7.3.2-1
- Update to 7.3.2 - http://www.php.net/releases/7_3_2.php

* Mon Feb 25 2019 Alexander Ursu <alexander.ursu@gmail.com> - 7.3.0-1
- update to 7.3.0 GA
- update FPM configuration from upstream
- bump API numbers
- switch from libpcre to libpcre2

* Wed Feb  6 2019 Remi Collet <remi@remirepo.net> - 7.2.15-1
- Update to 7.2.15 - http://www.php.net/releases/7_2_15.php

* Wed Feb  6 2019 Alexander Ursu <alexander.ursu@gmail.com> - 7.2.14-2
- fixed zend api RPM version

* Tue Jan  8 2019 Remi Collet <remi@remirepo.net> - 7.2.14-1
- Update to 7.2.14 - http://www.php.net/releases/7_2_14.php

* Sat Dec  8 2018 Remi Collet <remi@remirepo.net> - 7.2.13-2
- Fix null pointer dereference in imap_mail CVE-2018-19935

* Wed Dec  5 2018 Remi Collet <remi@remirepo.net> - 7.2.13-1
- Update to 7.2.13 - http://www.php.net/releases/7_2_13.php

* Wed Nov 21 2018 Remi Collet <remi@remirepo.net> - 7.2.13-0.1.RC1
- update to 7.2.13RC1

* Tue Nov  6 2018 Remi Collet <remi@remirepo.net> - 7.2.12-1
- Update to 7.2.12 - http://www.php.net/releases/7_2_12.php

* Fri Nov  2 2018 Remi Collet <remi@remirepo.net> - 7.2.12-0.1.RC1
- rebuild

* Tue Oct 23 2018 Remi Collet <remi@remirepo.net> - 7.2.12~RC1-1
- update to 7.2.12RC1

* Wed Oct 10 2018 Remi Collet <remi@remirepo.net> - 7.2.11-1
- Update to 7.2.11 - http://www.php.net/releases/7_2_11.php

* Tue Sep 11 2018 Remi Collet <remi@remirepo.net> - 7.2.10-1
- Update to 7.2.10 - http://www.php.net/releases/7_2_10.php

* Sun Sep  2 2018 Alexander Ursu <alexander.ursu@gmail.com> - 7.2.9-2
- Corrected ionCube extension (rpm build bug)

* Thu Aug 16 2018 Remi Collet <remi@remirepo.net> - 7.2.9-1
- Update to 7.2.9 - http://www.php.net/releases/7_2_9.php

* Tue Jul 17 2018 Remi Collet <remi@remirepo.net> - 7.2.8-1
- Update to 7.2.8 - http://www.php.net/releases/7_2_8.php
- FPM: add getallheaders, backported from 7.3

* Tue Mar 27 2018 Remi Collet <remi@remirepo.net> - 7.2.4-1
- Update to 7.2.4 - http://www.php.net/releases/7_2_4.php
- FPM: update default pool configuration for process.dumpable

* Wed Mar 21 2018 Remi Collet <remi@remirepo.net> - 7.2.4~RC1-3
- use systemd RuntimeDirectory instead of /etc/tmpfiles.d

* Wed Feb 28 2018 Remi Collet <remi@remirepo.net> - 7.2.3-1
- Update to 7.2.3 - http://www.php.net/releases/7_2_3.php
- FPM: revert pid file removal

* Wed Feb 14 2018 Remi Collet <remi@remirepo.net> - 7.2.3~RC1-1
- update to 7.2.3RC1
- adapt systzdata, fixheader and ldap_r patches
- apply upstream patch for date ext

* Tue Jan 30 2018 Remi Collet <remi@remirepo.net> - 7.2.2-1
- Update to 7.2.2 - http://www.php.net/releases/7_2_2.php

* Thu Jan 25 2018 Remi Collet <remi@remirepo.net> - 7.2.2~RC1-3
- undefine _strict_symbol_defs_build

* Wed Jan  3 2018 Remi Collet <remi@remirepo.net> - 7.2.1-1
- Update to 7.2.1 - http://www.php.net/releases/7_2_1.php

* Tue Nov 28 2017 Remi Collet <remi@remirepo.net> - 7.2.0-1
- update to 7.2.0 GA
- add upstream patch for https://bugs.php.net/75514

* Wed Nov 22 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.12-1
- upgrade to 7.1.12
- added process subpackage

* Mon Oct 02 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.10-1
- Update to 7.1.10 - http://www.php.net/releases/7_1_10.php

* Wed Sep 27 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.9-3
- disabled sockets extension
- added CGI scan directory

* Wed Sep 13 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.9-1
- Automatically load OpenSSL configuration file, from PHP 7.2
- Update to 7.1.9 - http://www.php.net/releases/7_1_9.php
- php-fpm: drop unneeded "pid" from default configuration
- disable httpd MPM check
- enable PHP execution of .phar files, see #1117140

* Tue Sep 12 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.6-4
- moved xmlrpc into php-common
- removed pgsql extension from CGI config

* Wed Jun 28 2017 Alexander Ursu <alexander.ursu@gmail.com> - 7.1.6-2
- made relocation feature optional (disabled by default)
- made fpm sapi optional (disabled by default)

* Wed Jun  7 2017 Remi Collet <remi@fedoraproject.org> - 7.1.6-1
- Update to 7.1.6 - http://www.php.net/releases/7_1_6.php
- add upstream security patches for oniguruma

* Tue Apr 11 2017 Remi Collet <remi@fedoraproject.org> - 7.1.4-1
- Update to 7.1.4 - http://www.php.net/releases/7_1_4.php

* Wed Mar 15 2017 Remi Collet <remi@fedoraproject.org> - 7.1.3-2
- remove %%attr, see #1432372

* Thu Nov 24 2016 Remi Collet <remi@fedoraproject.org> 7.0.13-2
- disable pcre.jit everywhere as it raise AVC #1398474

* Wed Nov  9 2016 Remi Collet <remi@fedoraproject.org> 7.0.13-1
- Update to 7.0.13 - http://www.php.net/releases/7_0_13.php
- update tzdata patch to v14, improve check for valid tz file

* Fri Jul 22 2016 Alexander Ursu <alexander.ursu@gmail.com> - 7.0.9-1
- Update to 7.0.9 - http://www.php.net/releases/7_0_9.php
- wddx: add upstream patch for https://bugs.php.net/72564

* Thu Jul 21 2016 Alexander Ursu <alexander.ursu@gmail.com> - 7.0.8-1
- initial build
