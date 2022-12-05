from SimpleLock import run_SL

file_input = input("Ketik nama file yang berada pada folder test: ")

try:
    run_SL(file_input)
except:
    print("Error with file inputted")

print("Metode Simple Locking Selesai")
