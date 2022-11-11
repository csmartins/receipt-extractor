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

purge-hortifruti:
	aws --endpoint-url http://localhost:4566 sqs purge-queue --queue-url http://localhost:4566/000000000000/hortifruti