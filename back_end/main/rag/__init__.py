from langchain.chains import LLMChain
from langchain.document_loaders import TextLoader
from langchain.llms.openai import OpenAI
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)
import sqlite3


class RAGApp:
    def __init__(self, collection_name='test_collection', embedding_dim=128):
        self.collection_name = collection_name
        self.embedding_dim = embedding_dim

        # Connect to SQLite database
        self.conn = sqlite3.connect(f'{collection_name}.db')
        self.c = self.conn.cursor()
        # Create documents table if it doesn't exist
        self.c.execute('''
            CREATE TABLE IF NOT EXISTS documents 
            (id INTEGER PRIMARY KEY, FilePath VarChar(256), content TEXT, summary TEXT)
        ''')
        self.conn.commit()

        # Setup Milvus connection
        connections.connect("default", host='localhost', port='19530')

        # Check if Milvus collection exists, else create one
        if not utility.has_collection(self.collection_name):
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim)
            ]
            schema = CollectionSchema(fields, description=f"{self.collection_name} schema")
            self.vector_db = Collection(name=self.collection_name, schema=schema)
        else:
            self.vector_db = Collection(name=self.collection_name)
            self.vector_db.load()


    def load_and_summarize(self, filepath):
        with open(filepath, 'r') as file:
            document = file.read()

        llm = OpenAI(api_key='your-api-key', temperature=0.7)
        summarizer = LLMChain(llm=llm, prompt="""Please summarize the code provided. Make sure to:
    
    Describe purpose of main constructor objects for context.
    Replace the function's code with a brief word summary. This summary might not need to be in plain language, but it should encapsulate all crucial and essential information of what the function does.
    Tag before function def using <tag></tag> the complexity of the function. (trivial, easy, medium, hard, vhard, extreme).
    Omit imports.
    Add an initial comment explaining the code's overall purpose and its potential use cases.
    No verbose or fill in tokens. No other text needed.
    
    Code: \n""")

        summary = summarizer.run(text=document)
        return [document], [summary]


    def embed_and_store(self, documents, summaries):
        for i, (doc, summary) in enumerate(zip(documents, summaries)):
            embedding = self.embeddings.embed_text(summary)
            with self.conn:
                self.conn.execute("INSERT INTO documents (content, summary) VALUES (?, ?)",
                                  (doc.page_content, summary))

            doc_id = self.conn.last_insert_rowid()
            self.vector_db.insert(self.repository_name, summary, embedding, id=doc_id)


    def search_most_similar(self, new_summary):
        new_summary_embedding = self.embeddings.embed_text(new_summary)
        results = self.vector_db.search(self.repository_name, new_summary_embedding)
        most_similar_id = results[0][0]
        return self.vector_db.search_by_id(self.repository_name, most_similar_id)


    def run(self):
        import os

        # List all .py files in the current directory (root of your application)
        python_files = [f for f in os.listdir() if f.endswith('.py')]

        for file in python_files:
            documents, summaries = self.load_and_summarize(file)
            self.embed_and_store(documents, summaries, file)


if __name__ == "__main__":
    repository = input("Enter the repository (collection) name: ")
    app = RAGApp(repository)
    app.run("documents.txt")
    app.close()
