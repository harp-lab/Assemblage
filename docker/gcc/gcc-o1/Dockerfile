FROM assemblage-gcc:base

# RUN echo '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' >> /gtoken
# RUN gh auth login --with-token < /gtoken

ENV CC='gcc'
ENV CXX='g++'

RUN echo '11:gcc' >> /conf

RUN mv /usr/bin/gcc /usr/bin/gccr && mv /usr/bin/g++ /usr/bin/g++r

RUN cp -f /assemblage/ccwrapper/wrap-gcc-o1.py /assemblage/ccwrapper/cc && \
    cp -f /assemblage/ccwrapper/wrap-gpp-o1.py /assemblage/ccwrapper/cc1plus && \
    chmod 777 /assemblage/ccwrapper/cc && chmod 777 /assemblage/ccwrapper/cc1plus && \
    cp -f /assemblage/ccwrapper/cc /usr/bin/clang && cp -f /assemblage/ccwrapper/cc /usr/bin/gcc && \
    cp -f /assemblage/ccwrapper/cc1plus /usr/bin/clang++ && cp -f /assemblage/ccwrapper/cc1plus /usr/bin/g++

WORKDIR /assemblage
