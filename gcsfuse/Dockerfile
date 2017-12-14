FROM golang:1-alpine
MAINTAINER tym@adops.com


VOLUME /save
RUN apk add --no-cache git
RUN go get github.com/googlecloudplatform/gcsfuse
RUN chmod +x /go/bin/gcsfuse

CMD cp /go/bin/gcsfuse /save
