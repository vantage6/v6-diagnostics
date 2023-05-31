#!/bin/sh

IMAGE=harbor.carrier-mu.src.surf-hosted.nl/carrier/n2n-diagnostics:test

echo $IMAGE

docker build -t $IMAGE .

docker push $IMAGE