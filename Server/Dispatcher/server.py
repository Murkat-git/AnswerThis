from operator import itemgetter

import weaviate
import weaviate.classes as wvc
from fastapi import FastAPI
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.prompts import ChatPromptTemplate
from langserve import add_routes
from pydantic.v1 import BaseModel, Field
from langserve import CustomUserType

DB_DOCUMENT = "Document"
DB_CHUNK = "Chunk"
client = weaviate.connect_to_local(host="weaviate")

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple api server using Langchain's Runnable interfaces",
)


@app.get("/tenants")
def get_tenants():
    return list(client.collections.get(DB_DOCUMENT).tenants.get().keys())


class RAGInputSchema(CustomUserType):
    tenant: str
    prompt: str


def get_context_from_db(inputs):
    tenant = inputs.tenant
    prompt = inputs.prompt
    rel_obj = (
        client.collections.get(DB_CHUNK)
        .with_tenant(tenant)
        .query.hybrid(
            prompt,
            alpha=0.75,
            limit=3,
            fusion_type=wvc.query.HybridFusion.RELATIVE_SCORE,
        )
        .objects
    )
    context = "\n".join([obj.properties["text"] for obj in rel_obj])
    return {"context": context, "question": prompt}


retriever = RunnableLambda(get_context_from_db)

# template = """You are a multilingual assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. You must write the answer in the same language as the given question. Keep the answer concise. If you don't know the answer, just say that you don't know.
# Question: '''{question}'''
# Context: '''{context}'''
# Answer:
# """
template = """You are a multilingual chat assistant. You must answer the questions based on the provided context. Keep your answers short and on point.
Context: {context}
Question: {question}
"""
prompt = ChatPromptTemplate.from_template(template)

llm = Ollama(model="llama3", base_url="http://ollama:11434", temperature=0.4, keep_alive=-1)


chain = retriever | prompt | llm | StrOutputParser()

add_routes(app, chain, path="/chain", input_type=RAGInputSchema)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
