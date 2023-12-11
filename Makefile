start-all-dependencies:
	docker-compose up -d

start-mongo:
	docker-compose up -d mongodb

start-localstack:
	docker-compose up -d localstack

start-opensearch:
	docker-compose up -d opensearch-node1 opensearch-node2 opensearch-dashboards

create-all-queues:
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name receipts --output text
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name receipts-error --output text
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name hortifruti --output text
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name hortifruti-error --output text
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name zonasul --output text
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name zonasul-error --output text

setup: start-all-dependencies
	pipenv run make create-all-queues
	pipenv shell

get-receipts-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/receipts --attribute-names All

get-hortifruti-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/hortifruti --attribute-names All

get-zonasul-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/zonasul --attribute-names All

get-receipts-error-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/receipts-error --attribute-names All

get-hortifruti-error-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/hortifruti-error --attribute-names All

get-zonasul-error-attributes:
	aws --endpoint-url http://localhost:4566 sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/zonasul-error --attribute-names All

purge-receipts:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/receipts

purge-hortifruti:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-zonasul:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/zonasul

purge-receipts-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/receipts-error

purge-hortifruti-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti-error

purge-zonasul-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/zonasul-error

build-hortifruti:
	docker build . -f hortifruti.Dockerfile
