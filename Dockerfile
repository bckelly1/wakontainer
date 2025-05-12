# file: flask_gunicorn_distroless.dockerfile

FROM python  AS build-env
WORKDIR /app

# First install packages to avoid re-run pip install
COPY --chown=nonroot:nonroot requirements.txt ./
RUN pip install --disable-pip-version-check -r requirements.txt --target /packages

COPY --chown=nonroot:nonroot app /app

FROM gcr.io/distroless/python3:latest
WORKDIR /app
COPY --chown=root:root --from=build-env /app /app
COPY --from=build-env /packages /packages
#instead of COPY --from=build-env /packages /usr/local/lib/python/site-packages

ENV PYTHONPATH=/packages
ENV WAKONTAINER_BIND_ADDRESS=0.0.0.0
ENV WAKONTAINER_PORT=80
ENV PATH="/packages:$PATH"
#instead of ENV PYTHONPATH=/usr/local/lib/python/site-packages

CMD ["wsgi.py"]