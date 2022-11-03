from opensearchpy import OpenSearch
import logging

logger = logging.getLogger(__name__)

def save_to_opensearch(host, port, user, password, product):

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

    # Create an index with non-default settings.
    index_name = 'products'
    # index_body = {
    #     'settings': {
    #         'index': {
    #         'number_of_shards': 4
    #         }
    #     }
    # }
    # print('\nCreating index:') 
    # response = client.indices.create(index_name, body=index_body)
    # print(response)

    logging.info("Save product to Opensearch")
    response = client.index(
        index = index_name,
        body = product,
        refresh = True
    )
    # TODO: better failure treatment
    # print(response)
