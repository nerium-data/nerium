IMAGE_REPO = us.gcr.io/lexical-cider-93918
SERVICE_NAME = $(shell basename $$(pwd))
COMMIT := $(shell git rev-parse --short HEAD)
IMAGE_TAG = $(IMAGE_REPO)/$(SERVICE_NAME):$(COMMIT)
TEST_COMMAND = true
TARGET_PORT = 8081
PATCH_FILE = patch.json


.PHONY: build
build:
	docker build -t $(IMAGE_TAG) .


.PHONY: test
test: build
	docker run -it $(IMAGE_TAG) $(TEST_COMMAND)


.PHONY: deploy
deploy: test cluster secret_path
	gcloud docker -- push $(IMAGE_TAG)
	kubectl apply -f $(SECRET_PATH)/pgbouncer/pgbouncer.yml
	kubectl create secret generic nerium-dotenv --from-file=$(SECRET_PATH)/nerium/.env
	kubectl run $(SERVICE_NAME) --image=$(IMAGE_TAG) --port=$(TARGET_PORT)
ifdef PATCH_FILE
	kubectl patch deployment $(SERVICE_NAME) --patch '$(subst {{service_name}},$(SERVICE_NAME),$(shell cat $(PATCH_FILE)))'
endif
	kubectl expose deployment $(SERVICE_NAME) --port=80 --target-port=$(TARGET_PORT)


.PHONY: clean
clean: cluster
	-docker rmi $(IMAGE_TAG)
	-kubectl delete deployment $(SERVICE_NAME)
	-kubectl delete service $(SERVICE_NAME)
	-kubectl delete secret nerium-dotenv
	-kubectl delete -f $(SECRET_PATH)/pgbouncer/pgbouncer.yml


.PHONY: cluster
cluster:
ifndef CLUSTER
	$(error CLUSTER is undefined)
endif
	-gcloud container clusters create $(CLUSTER) \
		--preemptible \
		--enable-autoscaling \
		--num-nodes 1 \
		--min-nodes 0 \
		--max-nodes 5 \
		--scopes https://www.googleapis.com/auth/cloud_debugger
	gcloud container clusters get-credentials $(CLUSTER)


.PHONY: secret_path
secret_path:
ifndef SECRET_PATH
	$(error SECRET_PATH is undefined)
endif


# Pipenv commands
.PHONY: install
install: build
	docker run -it -v $(shell pwd):$(shell docker run $(IMAGE_TAG) pwd) $(IMAGE_TAG) pipenv install $(PACKAGE)


.PHONY: uninstall
uninstall: build
	docker run -it -v $(shell pwd):$(shell docker run $(IMAGE_TAG) pwd) $(IMAGE_TAG) pipenv uninstall $(PACKAGE)


.PHONY: lock
lock: build
	docker run -it -v $(shell pwd):$(shell docker run $(IMAGE_TAG) pwd) $(IMAGE_TAG) pipenv lock


.venv: build
	docker run -it -v $(shell pwd):$(shell docker run $(IMAGE_TAG) pwd) $(IMAGE_TAG) pipenv --three


# httpie command
.PHONY: http
http: cluster
	kubectl run -it --rm httpie-$(shell whoami)-$$RANDOM --image=clue/httpie --restart=Never --command bash
