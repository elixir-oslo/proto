RELEASE_CURR:=16.01
RELEASE_CURR_MINOR_NEXT:=$(shell expr `awk '$$1 == "VERSION_MINOR" {print $$NF}' lib/galaxy/version.py | tr -d \" | sed 's/None/0/' ` + 1)
RELEASE_NEXT:=16.04
# TODO: This needs to be updated with create_release_rc
#RELEASE_NEXT_BRANCH:=release_$(RELEASE_NEXT)
RELEASE_NEXT_BRANCH:=dev
RELEASE_UPSTREAM:=upstream
GRUNT_DOCKER_NAME:=galaxy/client-builder:16.01

all:
	@echo "This makefile is primarily used for building Galaxy's JS client. A sensible all target is not yet implemented."

npm-deps:
	cd client && npm install

grunt: npm-deps
	cd client && node_modules/grunt-cli/bin/grunt

style: npm-deps
	cd client && node_modules/grunt-cli/bin/grunt style

webpack: npm-deps
	cd client && node_modules/webpack/bin/webpack.js -p

client: grunt style webpack

grunt-docker-image:
	docker build -t ${GRUNT_DOCKER_NAME} client

grunt-docker: grunt-docker-image
	docker run -it -v `pwd`:/data ${GRUNT_DOCKER_NAME}

clean-grunt-docker-image:
	docker rmi ${GRUNT_DOCKER_NAME}


# Release Targets
create_release_rc:
	git checkout dev
	git pull --ff-only ${RELEASE_UPSTREAM} dev
	git push origin dev
	git checkout -b release_$(RELEASE_CURR)
	git push origin release_$(RELEASE_CURR)
	git push ${RELEASE_UPSTREAM} release_$(RELEASE_CURR)
	git checkout -b version-$(RELEASE_CURR)
	sed -i "s/^VERSION_MAJOR = .*/VERSION_MAJOR = \"$(RELEASE_CURR)\"/" lib/galaxy/version.py
	sed -i "s/^VERSION_MINOR = .*/VERSION_MINOR = \"rc1\"/" lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Update version to $(RELEASE_CURR).rc1"
	git checkout dev

	git checkout -b version-$(RELEASE_NEXT).dev
	sed -i "s/^VERSION_MAJOR = .*/VERSION_MAJOR = \"$(RELEASE_NEXT)\"/" lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Update version to $(RELEASE_NEXT).dev"

	-git merge version-$(RELEASE_CURR)
	git checkout --ours lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Merge branch 'version-$(RELEASE_CURR)' into version-$(RELEASE_NEXT).dev"
	git push origin version-$(RELEASE_CURR):version-$(RELEASE_CURR)
	git push origin version-$(RELEASE_NEXT).dev:version-$(RELEASE_NEXT).dev
	git branch -d version-$(RELEASE_CURR)
	git branch -d version-$(RELEASE_NEXT).dev

create_release:
	git pull --ff-only $(RELEASE_UPSTREAM) master
	git push origin master
	git checkout release_$(RELEASE_CURR)
	git pull --ff-only $(RELEASE_UPSTREAM) release_$(RELEASE_CURR)
	#git push origin release_$(RELEASE_CURR)
	git checkout dev
	git pull --ff-only $(RELEASE_UPSTREAM) dev
	#git push origin dev
	# Test run of merging. If there are conflicts, it will fail here here.
	git merge release_$(RELEASE_CURR)
	git checkout release_$(RELEASE_CURR)
	sed -i "s/^VERSION_MINOR = .*/VERSION_MINOR = None/" lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Update version to $(RELEASE_CURR)"
	git tag -m "Tag version $(RELEASE_CURR)" v$(RELEASE_CURR)

	git checkout dev
	-git merge release_$(RELEASE_CURR)
	git checkout --ours lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Merge branch 'release_$(RELEASE_CURR)' into dev"
	git checkout master
	git merge release_$(RELEASE_CURR)
	#git push origin release_$(RELEASE_CURR):release_$(RELEASE_CURR)
	#git push origin dev:dev
	#git push origin master:master
	#git push origin --tags

create_point_release:
	git pull --ff-only $(RELEASE_UPSTREAM) master
	git push origin master
	git checkout release_$(RELEASE_CURR)
	git pull --ff-only $(RELEASE_UPSTREAM) release_$(RELEASE_CURR)
	#git push origin release_$(RELEASE_CURR)
	git checkout $(RELEASE_NEXT_BRANCH)
	git pull --ff-only $(RELEASE_UPSTREAM) $(RELEASE_NEXT_BRANCH)
	#git push origin $(RELEASE_NEXT_BRANCH)
	git merge release_$(RELEASE_CURR)
	git checkout release_$(RELEASE_CURR)
	sed -i "s/^VERSION_MINOR = .*/VERSION_MINOR = \"$(RELEASE_CURR_MINOR_NEXT)\"/" lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Update version to $(RELEASE_CURR).$(RELEASE_CURR_MINOR_NEXT)"
	git tag -m "Tag version $(RELEASE_CURR).$(RELEASE_CURR_MINOR_NEXT)" v$(RELEASE_CURR).$(RELEASE_CURR_MINOR_NEXT)
	git checkout $(RELEASE_NEXT_BRANCH)
	-git merge release_$(RELEASE_CURR)
	git checkout --ours lib/galaxy/version.py
	git add lib/galaxy/version.py
	git commit -m "Merge branch 'release_$(RELEASE_CURR)' into $(RELEASE_NEXT_BRANCH)"
	git checkout master
	git merge release_$(RELEASE_CURR)
	#git push origin release_$(RELEASE_CURR):release_$(RELEASE_CURR)
	#git push origin $(RELEASE_NEXT_BRANCH):release_$(RELEASE_NEXT_BRANCH)
	#git push origin master:master
	#git push origin --tags
	git checkout release_$(RELEASE_CURR)