#
# Interface versions exposed by PHP:
#
%php_core_api @PHP_APIVER@
%php_zend_api @PHP_ZENDVER@
%php_pdo_api  @PHP_PDOVER@
%php_version  @PHP_VERSION@

%php_extdir    %{_libdir}/php85/modules

%php_inidir    %{_sysconfdir}/php85/php.d

%php_incldir    %{_includedir}/php85

%__php         %{_bindir}/php85

%__phpize      %{_bindir}/phpize85

%__phpconfig    %{_bindir}/php85-config

%pecl_xmldir   %{_sharedstatedir}/php85/peclxml
