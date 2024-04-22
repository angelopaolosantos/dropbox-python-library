import os
import dropbox
import dropbox.files
import hashlib

def upload_all_local_files():
    for file in os.listdir("local_files"):
        with open(os.path.join("local_file", file), "rb") as f:
            data = f.read()
            dbx.files_upload(data, f"/{file}")

def download_all_cloud_files():
    for entry in dbx.files_list_folder("").entries:
        dbx.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")

def dropbox_content_hash(file):
    hash_chunk_size = 4 * 1024 * 1024
    with open(file, "rb") as f:
        block_hashes = bytes()
        while True:
            chunk = f.read(hash_chunk_size)
            if not chunk:
                break
            block_hashes += hashlib.sha256(chunk).digest()
        return hashlib.sha256(block_hashes).hexdigest()
    
def download_changed():
    for entry in dbx.files_list_folder("").entries:
        if os.path.exists(os.path.join("local_files", entry.name)):
            local_hash = dropbox_content_hash(os.path.join("local_files", entry.name))
            if local_hash != entry.content_hash:
                print("FILE HAS CHANGED: ", entry.name)
                dbx.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")
            else:
                print("UNCHANGED:", entry.name)
        else:
            print("NEW FILE:", entry.name)
            dbx.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")


def upload_changed():
    cloud_files = {e.name: e.content_hash for e in dbx.files_list_folder("").entries}
    for file in os.listdir("local_files"):
        if file in cloud_files.keys():
            local_hash = dropbox_content_hash(os.path.join("local_files", file))
            if local_hash != cloud_files[file]:
                print("FILE CHANGED:", file)
                with open(os.path.join("local_files", file), "rb") as f:
                    data = f.read()
                    dbx.files_upload(data, f"{file}", mode=dropbox.files.WiteMode("overwrite"))
            else:
                print("UNCHANGED:", file)
        else:
            print("NEW FILE:", file)
            with open(os.path.join("local_files", file), "rb") as f:
                    data = f.read()
                    dbx.files_upload(data, f"{file}", mode=dropbox.files.WiteMode("overwrite"))
    
    
    for entry in dbx.files_list_folder("").entries:
        if os.path.exists(os.path.join("local_files", entry.name)):
            local_hash = dropbox_content_hash(os.path.join("local_files", entry.name))
            if local_hash != entry.content_hash:
                print("FILE HAS CHANGED: ", entry.name)
                dbx.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")
            else:
                print("UNCHANGED:", entry.name)
        else:
            print("NEW FILE:", entry.name)
            dbx.files_download_to_file(os.path.join("local_files", entry.name), f"/{entry.name}")


with open("token_dropbox.txt", "r") as f:
    TOKEN = f.read()

dbx =  dropbox.Dropbox(TOKEN)

for entry in dbx.files_list_folder("").entries:
    print(entry)