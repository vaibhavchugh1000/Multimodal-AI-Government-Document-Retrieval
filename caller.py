from user_pipeline import user_query_pipeline
from admin_pipeline import process_document
from vector_store import collection



id=str(input("enter id :"))
password=str(input("enter password : "))

if id=="user" and password=="user" : 
    query=str(input("enter your query : "))
    result=user_query_pipeline(query)
    
    print("assistant answer : ",result["answer"])
    print()
    print("language : ",result["language"])
    print()
    print("query : ",query)
    print()
    print("sources : ",result["sources"])

elif id=="admin" and password=="admin":
    document_path=str(input("pls enter document_path : "))
    result=process_document(document_path)
    print(result)
