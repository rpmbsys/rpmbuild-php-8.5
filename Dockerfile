ARG os=10.1.20251126
FROM aursu/php85build:${os}-base

COPY SOURCES ${BUILD_TOPDIR}/SOURCES
COPY SPECS ${BUILD_TOPDIR}/SPECS

RUN chown -R $BUILD_USER ${BUILD_TOPDIR}/{SOURCES,SPECS}

USER $BUILD_USER
ENTRYPOINT ["/usr/bin/rpmbuild", "php.spec", "--with", "cgi", "--with", "fpm"]
CMD ["-ba"]
