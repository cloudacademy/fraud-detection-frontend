From alpine:3.5
MAINTAINER CloudAcademy <jeremy.cook@cloudacademy.com>

RUN echo "http://dl-4.alpinelinux.org/alpine/v3.5/main" >> /etc/apk/repositories && \
	echo "http://dl-4.alpinelinux.org/alpine/v3.5/community" >> /etc/apk/repositories

# application folder
ENV APP_DIR /app
ENV SRC_DIR /src

# update source
RUN apk update && \
	apk add python py-pip supervisor git && \
	pip install --upgrade pip && \
	pip install Flask && \
	pip install flask-cors && \
	pip install gunicorn && \
	pip install requests && \
	pip install pymysql && \
	mkdir -p ${SRC_DIR} && \	
	mkdir -p ${APP_DIR}/web && \
	mkdir -p ${APP_DIR}/conf && \
	mkdir -p ${APP_DIR}/logs && \
	rm -rf /var/cache/apk/* && \
	echo "files = ${APP_DIR}/conf/*.ini" >> /etc/supervisord.conf

RUN git clone https://github.com/cloudacademy/fraud-detection-frontend ${SRC_DIR}

RUN cp -R ${SRC_DIR}/app/* ${APP_DIR}

VOLUME ["${APP_DIR}"]

EXPOSE 5000

CMD ["supervisord", "-c", "/etc/supervisord.conf"]