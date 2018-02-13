deploy-results: check_secret
	gcloud container clusters get-credentials playground
	gcloud docker -a

	docker build -t us.gcr.io/lexical-cider-93918/nerium:latest .
	docker push us.gcr.io/lexical-cider-93918/nerium:latest
	kubectl create secret generic nerium-dotenv --from-file=$(SECRET_PATH)nerium/.env
	kubectl create -f nerium-k8s.yml
	kubectl set image deployments/nerium nerium=us.gcr.io/lexical-cider-93918/nerium:latest

	kubectl expose deployment nerium --name=results --type=NodePort --port=80 --target-port=8081

destroy-results:
	gcloud container clusters get-credentials playground
	kubectl delete deployment nerium
	kubectl delete service nerium
	kubectl delete secret nerium-dotenv

check_secret:
ifndef SECRET_PATH
	$(error SECRET_PATH is undefined)
endif
