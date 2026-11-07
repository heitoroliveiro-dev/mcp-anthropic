from pydantic import Field
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")


docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

@mcp.tool(
    name="read_doc_contents",
    description="Read the contents of a document and return it as a string."
)
def read_documents(
    doc_id: str = Field(description="Id of the document to read")
):
    if doc_id not in docs:
        raise ValueError(f'Doc with id {doc_id} not found')    

    return docs[doc_id]

@mcp.tool(
    name="edit_document",
    description="Edit a document by replacing a string in the documents content with a new string."
)
def edit_document(
    doc_id: str = Field(description="Id of the document that will be edited"),
    old_str: str = Field(description="The text to replace. Must match exactly, including whitespace"),
    new_str: str = Field(description="The new text to insert in place of the old text")
):
    if doc_id not in docs:
        raise ValueError(f'Doc with id {doc_id}not found')

    docs[doc_id] = docs[doc_id].replace(old_str, new_str)

#------------- Build a list of resources
@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())

#------------- Return the content of a doc
@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id:str):
    if doc_id not in docs:
        raise ValueError(f'Doc with id {doc_id} not found')
    return docs[doc_id]

@mcp.prompt(
    name="list_prompts",
    description="List available prompts when user type /"
)
def list_prompts() -> list[str]:
    return list(docs.keys())

@mcp.prompt(
    name="format",
    description="Rewrite a doc in markdown format."
)
def format_doc(doc_id: str = Field(description="Id of the document that will be edited")) -> list[base.Message]:
    prompt = f"""
    Rewrite the <document_id>{doc_id}</document_id> in markdown.
    Use titles, list and tables when makes sense.
    Use tools edit_document to save the result
    """
    return [base.UserMessage(prompt)]

def summarize_doc(doc_id: str = Field(description="Id of the document that will be summarized")) -> list[base.Message]:
    prompt = f"""
    Summarize the <document_id>{doc_id}</document_id>.
    Use titles, list and tables when makes sense.
    Use tools edit_document to save the result
    """
    return [base.UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
