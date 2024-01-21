FROM assemblage-clang:base

# TODO: we should be running these outside of the build step
#       to account for multiple tokens.
# RUN echo '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' >> /gtoken
# RUN gh auth login --with-token < /gtoken

ENV CC='cc'
ENV CXX='cc1plus'

RUN echo '12:clang' >> /conf

RUN mv /usr/bin/clang /usr/bin/clangr && mv /usr/bin/clang++ /usr/bin/clang++r

RUN cp -f /assemblage/ccwrapper/wrap-clang-o1.py /assemblage/ccwrapper/cc && \
    cp -f /assemblage/ccwrapper/wrap-clangpp-o1.py /assemblage/ccwrapper/cc1plus && \
    chmod 777 /assemblage/ccwrapper/cc && chmod 777 /assemblage/ccwrapper/cc1plus && \
    cp /assemblage/ccwrapper/cc /usr/bin/cc && cp /assemblage/ccwrapper/cc1plus /usr/bin/cc1plus && \
    cp -f /assemblage/ccwrapper/cc /usr/bin/clang && cp -f /assemblage/ccwrapper/cc /usr/bin/gcc && \
    cp -f /assemblage/ccwrapper/cc1plus /usr/bin/clang++ && cp -f /assemblage/ccwrapper/cc1plus /usr/bin/g++

WORKDIR /assemblage

