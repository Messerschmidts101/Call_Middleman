import glob, os

# Construct the directory path from components
strContextKnowledgeDirectory = os.path.join(
    "Website", "Database", "User_Knowledge_Base", "test_4", "chroma_embeddings"
)

# Verify constructed path
print(f"Constructed Directory Path: {strContextKnowledgeDirectory}")

# Check if the directory exists and list its contents
if os.path.isdir(strContextKnowledgeDirectory):
    print("Directory exists. Listing contents...")
    for root, dirs, files in os.walk(strContextKnowledgeDirectory):
        print(f"Root: {root}, Dirs: {dirs}, Files: {files}")

# Use glob to search for .txt files in the directory recursively
text_files = glob.glob(os.path.join(strContextKnowledgeDirectory, "**", "*.txt"), recursive=False)
print('Text Files Found: ', text_files)

# Check if no files are found
if not text_files:
    print("No .txt files found in the directory. Please ensure the path is correct and files are present.")
