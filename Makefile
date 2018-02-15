deploy:
	docker build -f Testenv -t neriumtestenv .
	docker run -it neriumtestenv python tests.py
	gcloud app deploy

todo:
	grep -r "TODO" .

#integrate:
# pull the current branch
# pull master
# build
# run tests
# push to current branch
# some day make sure there is feedback from CI on the build

#pull:
# pull the current branch
# pull master

#test:


