start-all-dependencies:
	docker-compose up -d

create-all-queues:
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name receipts
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name receipts-error
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name hortifruti
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name hortifruti-error
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name zonasul
	aws --endpoint-url http://localhost:4566 sqs create-queue --queue-name zonasul-error

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
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-hortifruti:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-zonasul:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-receipts-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-hortifruti-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

purge-zonasul-error:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti

build-hortifruti:
	docker build . -f hortifruti.Dockerfile
