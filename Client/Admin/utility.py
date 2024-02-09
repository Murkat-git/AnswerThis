import re
import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from st_files_connection import FilesConnection
from unstructured.partition.auto import partition
import streamlit as st

DB_DOCUMENT = "Document"
DB_CHUNK = "Chunk"

SOFT_MAX_CHUNK = 300
MAX_CHUNK = 400
OVERLAP = 50


pattern = re.compile("^[a-zA-Z0-9_]*$")


def check_naming(string):
    return pattern.match(string)


@st.cache_resource(show_spinner="Connecting to file system")
def get_file_client():
    return st.connection("file_connection", type=FilesConnection)


def process_file(filename, raw, tenant):
    if file_exists(filename):
        delete_document(filename, tenant)
    write_file(filename, raw)

    doc_uuid = write_doc_db(filename, tenant)
    chunks = partition(
        filename,
        new_after_n_chars=SOFT_MAX_CHUNK,
        max_characters=MAX_CHUNK,
        overlap=OVERLAP,
    )
    write_chunks_db(doc_uuid, chunks, tenant)


def write_file(filename, raw):
    conn = get_file_client()
    conn.fs.pipe(filename, raw)


def file_exists(filename):
    conn = get_file_client()
    return conn.fs.exists(filename)


def delete_document(filename, tenant):
    conn = get_file_client()
    conn.fs.rm(filename)
    delete_document_db(filename, tenant)


@st.cache_resource(show_spinner="Connecting to the database")
def get_db_client():
    return weaviate.connect_to_local(host="weaviate")


def create_db():
    client = get_db_client()
    document_collection_name = DB_DOCUMENT
    chunk_collection_name = DB_CHUNK
    client.collections.create(
        name=document_collection_name,
        multi_tenancy_config=wvc.config.Configure.multi_tenancy(True),
        vectorizer_config=wvc.config.Configure.Vectorizer.none(),
        properties=[
            wvc.config.Property(name="doc_name", data_type=wvc.config.DataType.TEXT),
        ],
    )
    client.collections.create(
        name=chunk_collection_name,
        multi_tenancy_config=wvc.config.Configure.multi_tenancy(True),
        vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_transformers(),
        properties=[
            wvc.config.Property(name="text", data_type=wvc.config.DataType.TEXT)
        ],
        references=[
            wvc.config.ReferenceProperty(
                name="doc_uuid", target_collection=document_collection_name
            )
        ],
    )


def create_tenant(name):
    tenant = wvc.tenants.Tenant(name=name)
    client = get_db_client()
    client.collections.get(DB_DOCUMENT).tenants.create(tenants=[tenant])
    client.collections.get(DB_CHUNK).tenants.create(tenants=[tenant])


def get_tenants():
    client = get_db_client()
    return client.collections.get(DB_DOCUMENT).tenants.get().keys()


def write_doc_db(filename, tenant):
    client = get_db_client()
    doc_collection = client.collections.get(DB_DOCUMENT).with_tenant(tenant)
    return doc_collection.data.insert(
        properties={"doc_name": filename}, uuid=generate_uuid5(filename)
    )


def write_chunks_db(doc_uuid, chunks, tenant):
    client = get_db_client()
    chunk_collection = client.collections.get(DB_CHUNK).with_tenant(tenant)
    print(chunks)
    for chunk in chunks:
        chunk_collection.data.insert(
            properties={"text": str(chunk)}, references={"doc_uuid": doc_uuid}
        )


def delete_document_db(filename, tenant):
    client = get_db_client()
    doc_uuid = generate_uuid5(filename)

    client.collections.get(DB_CHUNK).with_tenant(tenant).data.delete_many(
        where=wvc.query.Filter.by_property("doc_uuid").equal(doc_uuid), verbose=True
    )
    client.collections.get(DB_DOCUMENT).with_tenant(tenant).data.delete_by_id(doc_uuid)


def get_all_chunks(tenant, limit=100):
    client = get_db_client()
    return client.collections.get(DB_CHUNK).with_tenant(tenant).query.fetch_objects(include_vector=True, limit=limit)
