FROM assemblage-clang:base

# RUN echo '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' >> /gtoken
# RUN gh auth login --with-token < /gtoken

ENV CC='clang'
ENV CXX='clang++'

RUN echo '2:clang' >> /conf

RUN cp /usr/bin/clang /usr/bin/cc && cp /usr/bin/clang++ /usr/bin/cc1plus && \
    cp -f /usr/bin/clang /usr/bin/gcc && cp -f /usr/bin/clang++ /usr/bin/g++

WORKDIR /assemblage

