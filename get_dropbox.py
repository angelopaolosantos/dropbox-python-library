import dropbox
import os
import shutil
import hashlib
import types
import atexit

import pickle # for data persistence
import time


# Find folder ID
def get_folders(dbx, folder):
    result = dbx.files_list_folder(folder, recursive=True)
    
    folders=[]
    
    def process_dirs(entries):
        print("Processing Directories...")
        for entry in entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                print("FOUND FOLDER:", entry.name)
                folders.append(entry.path_lower + '--> ' + entry.id)
    
    process_dirs(result.entries)
               
    while result.has_more:
        result = dbx.files_list_folder_continue(result.cursor)
        process_dirs(result.entries)
        
    return(folders)

def wipe_dir(download_dir):
    # wipe download dir
    try:
        shutil.rmtree(download_dir) 
    except:
        1+1

def get_files(dbx, folder_id, download_dir, check_hash = False):
    file_list = []

    # determine highest common directory
    # assert(result.entries[0].id==folder_id)
    # common_dir = result.entries[0].path_lower
    common_dir = ""

    #reload object from file
    if os.path.isfile(r'file_list.pkl'):
        with open(r'file_list.pkl', 'rb') as file:
            try:
                file_list = pickle.load(file)
                file.close()
            except:
                pass
        
    if file_list == []:
        # assert(folder_id.startswith('id:')) # Remove to allow empty "" for root folder
        result = dbx.files_list_folder(folder_id, recursive=True)
        
        
        
        def process_entries(entries):
            for entry in entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    #  file_list.append(entry.path_lower)
                    print("FOUND FILE:", entry.path_lower)
                    new_entry = types.SimpleNamespace()
                    new_entry.path_lower = entry.path_lower
                    new_entry.done = False
                    new_entry.content_hash = entry.content_hash
                    file_list.append(new_entry)
        
        process_entries(result.entries)
        
        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
        
            process_entries(result.entries)

        with open(r'file_list.pkl', 'wb') as file:
            pickle.dump(file_list, file)
            file.close

        # Create a backup file
        with open(r'file_list_bak.pkl', 'wb') as file:
            pickle.dump(file_list, file)
            file.close

    
    def exit_handler():
        # Save file on exit, interrupted or error occured     
        print("USER INTERRUPTED, SAVING file_list.pkl")  
        with open(r'file_list.pkl', 'wb') as file:
            pickle.dump(temp_file_list, file)
            file.close() 
        exit()

    atexit.register(exit_handler)
    
         
    print('Downloading ' + str(len(file_list)) + ' files...')
    i=0
    temp_file_list = file_list

    for index, fn in enumerate(file_list):
        i+=1
        printProgressBar(i, len(file_list))
        path = remove_suffix(download_dir, '/') + remove_prefix(fn.path_lower, common_dir).replace(":", "-").replace("|", "-").replace("\"", "-").replace("?", "")

        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)))
        except:
            1+1

        
        # Checked hash

        if hasattr(fn, 'done') and fn.done == True:
            print("SKIPPING FILE:", fn.path_lower)
        elif (fn.path_lower.endswith(".web")):
            print("SKIPPING FILE:", fn.path_lower)
        else:
            if os.path.exists(path):
                if check_hash == True:
                    local_hash = dropbox_content_hash(path)
                    print(fn.content_hash)
                    if local_hash != fn.content_hash:
                        print("FILE HAS CHANGED: ", fn.path_lower)
                        try:
                            dbx.files_download_to_file(path, fn.path_lower)
                        except:
                            print("FAILED TO DOWNLOAD:", fn.path_lower)
                            exit_handler()
                            continue
                    else:
                        print("UNCHANGED:", fn.path_lower)
                else:
                    print("UNCHANGED:", fn.path_lower)
            else:
                tries = 0
                while tries < 3:
                    print("NEW FILE:", fn.path_lower)
                    try:
                        dbx.files_download_to_file(path, fn.path_lower)
                        break
                    except:                    
                        print("FAILED TO DOWNLOAD:", fn.path_lower)
                        tries = tries + 1
                        time.sleep(5)
                        continue
                
                if tries == 3:
                    exit()

            
            temp_file_list[index].done = True
            print("SETTING ATTRIBUTE DONE:", fn.path_lower)  
            

# auxilary function to print iterations progress (from https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console)
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


# inspired by https://stackoverflow.com/questions/16891340/remove-a-prefix-from-a-string and 
# https://stackoverflow.com/questions/1038824/how-do-i-remove-a-substring-from-the-end-of-a-string-in-python
        
def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]

def remove_suffix(text, suffix):
    return text[:-(text.endswith(suffix) and len(suffix))]

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