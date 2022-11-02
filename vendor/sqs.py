import queue
import boto3
import logging
import os
import configparser


from botocore.exceptions import ClientError


logger = logging.getLogger(__name__)

config = configparser.ConfigParser()
config.read("config.ini")
sqs = boto3.client("sqs", endpoint_url=config["localstack"]["endpoint"])

def get_queue_info(queue_url):
    try:
        queue_attr = sqs.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['All']
        )
        return queue_attr
    except ClientError as error:
        logger.exception("Couldn't receive messages from queue url: %s", queue_url)
        raise error

def get_one_message(queue_url):
    try:
        messages = sqs.receive_message(
            QueueUrl=queue_url,
            MessageAttributeNames=['All'],
            MaxNumberOfMessages=1,
            WaitTimeSeconds=10
        )
        for message in messages['Messages']:
            print(message)
            logger.info("Received message: %s: %s", message['MessageId'], message['Body'])
    except ClientError as error:
        logger.exception("Couldn't receive any messages using queue URL: %s", queue_url)
        raise error
    except AttributeError as error:
        logger.info("No messages in the queue")
        return None
    else:
        return message

def send_one_message(queue_url, message_body, message_attributes=None):
    if not message_attributes:
        message_attributes = {}
    
    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message_body,
            MessageAttributes=message_attributes
        )
    except ClientError as error:
        logger.exception("Send message to %s failed: %s", queue_url, message_body)
        raise error
    else:
        return response

def delete_message(queue_url, handle):
    try:
        queue_attr = sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=handle
        )
        return queue_attr
    except ClientError as error:
        logger.exception("Couldn't delete message %s from queue url: %s", handle, queue_url)
        raise error
