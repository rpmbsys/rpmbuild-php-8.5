ARG os=10.2.20260525.0
FROM aursu/php85build:${os}-base

COPY SOURCES ${BUILD_TOPDIR}/SOURCES
COPY SPECS ${BUILD_TOPDIR}/SPECS

RUN chown -R $BUILD_USER ${BUILD_TOPDIR}/{SOURCES,SPECS}

USER $BUILD_USER
ENTRYPOINT ["/usr/bin/rpmbuild", "php.spec", "--with", "cgi", "--with", "fpm"]
CMD ["-ba"]
