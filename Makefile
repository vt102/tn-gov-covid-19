# see also https://aws.amazon.com/blogs/infrastructure-and-automation/aws-cloudformation-custom-resource-creation-with-python-aws-lambda-and-crhelper/
# see also https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-awscli.html#with-userapp-walkthrough-custom-events-create-iam-role

ZIPFILE  = tn-gov-covid-19-`git rev-parse --short HEAD`.zip


all: build

# install: build
# 	aws lambda update-function-code \
# 		--function-name "darksail" \
# 		--zip-file fileb://../darksail.zip 


build: get_count.py
	-rm ${ZIPFILE}
	pip install --target ./packages beautifulsoup4==4.8.2 bs4==0.0.1 boto3==1.12.21
	cd packages && zip -r9 ../${ZIPFILE} . && cd ..
	zip -g ${ZIPFILE} get_count.py

upload: build
	[ -z "${ACCTID}" ] && exit 1 || echo 0
	aws s3 cp ${ZIPFILE} "s3://deploy-${ACCTID}/lambda/"
