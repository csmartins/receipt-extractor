from opensearchpy import OpenSearch
from opensearchpy.exceptions import RequestError
import logging

logger = logging.getLogger(__name__)

def save_to_opensearch(host, port, user, password, index_name, data):

    try:
        client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (user, password),
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
            # ca_certs = ca_certs_path
        )

        logging.info("Save product to Opensearch")
        response = client.index(
            index = index_name,
            body = data,
            refresh = True
        )
        client.close()
    except Exception as er:
        logging.critical("Failed to save on Opensearch")
        logging.exception(er)

def create_index(host, port, user, password, index_name, mapping=None):

    try:
        client = OpenSearch(
            hosts = [{'host': host, 'port': port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (user, password),
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False,
            # ca_certs = ca_certs_path
        )
        
        logging.debug('Creating opensearch index') 
        response = client.indices.create(index_name, body=mapping)
        logging.debug(response)

        client.close()
    except RequestError as er:
        if "resource_already_exists_exception" in er.error:
            return
        else:
            logging.critical("Failed to create index")
            logging.exception(er)
            raise er
