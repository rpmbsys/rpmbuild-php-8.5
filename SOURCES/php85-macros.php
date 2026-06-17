#
# Interface versions exposed by PHP:
#
%php_core_api @PHP_APIVER@
%php_zend_api @PHP_ZENDVER@
%php_pdo_api  @PHP_PDOVER@
%php_version  @PHP_VERSION@

%php_extdir    %{_libdir}/php84/modules

%php_inidir    %{_sysconfdir}/php84/php.d

%php_incldir    %{_includedir}/php84

%__php         %{_bindir}/php84

%__phpize      %{_bindir}/phpize84

%__phpconfig    %{_bindir}/php84-config

%pecl_xmldir   %{_sharedstatedir}/php84/peclxml
