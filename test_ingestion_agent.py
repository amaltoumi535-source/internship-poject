from app.modules.ingestion.agent import ingest_file_tool

result = ingest_file_tool.invoke({
    "file_path": r"C:\Users\ADMIN\Downloads\testing ingestion upload.txt"
})
print(result)