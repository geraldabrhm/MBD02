import Util
import os
import time

class OCCTransaction():
    def __init__(self, id):
        self.id = id
        self.write_set = []
        self.read_set = []
        # self.temporaryData = []

        self.START = None
        self.TS = None
        self.FINISH = None

# Handle display message in read_phase
def read(data: str, isRead: bool, txnId: int):
    if(isRead):
        print(f"[READ PHASE T{txnId}] Read {data} from database and store it in local data version T{txnId}")
    else:
        print(f"[READ PHASE T{txnId}] Read {data} from database and store it in local data version T{txnId}, also write a value of {data} in local data version T{txnId}")

# ! Debug tool
# def printTxnsTimestamp(txn: list):
#     for val in(txn):
#         print(f"Transaction T{val.id}:")
#         print(f"START READ AND EXECUTION: {val.START}")
#         print(f"START VALIDATE: {val.TS}")
#         print(f"FINISH VALIDATE AND COMMIT: {val.FINISH}\n")

if __name__ == "__main__":
    file_name = input("Masukan nama file: ") # TODO change to file-based input
    numTxn = None # Number of transaction
    dataTxn = [] # Data affected in all transactions (schedule)
    txnSequence = [] # Sequence of context switch between transaction
    validatedTxnId = []

    txn = []

    # * FILE HANDLER
    ROOT_DIR = os.path.dirname(__file__)
    REL_PATH = f"fileinput\{file_name}" # TODO change to file-based input
    ABS_PATH = os.path.join(ROOT_DIR, REL_PATH)

    with open(ABS_PATH, 'r') as tx_file:
        # * Iterate through lines
        for (idx, line) in enumerate(tx_file):
            if(idx == 0):
                numTxn = int(line)
                # Create transaction instance
                for i in range(numTxn):
                    newTxn = OCCTransaction(i + 1)
                    txn.append(newTxn)
            elif(idx == 1):
                data = line.split(' ')
                for val in data:
                    dataTxn.append(val[0])
            else:
                txnSequence.append(line.rstrip('\n'))
                txnType, txnId, dataAffected = Util.parseTxnElmt(line.rstrip('\n'))
                if(txnType == 'R'): # txnType
                    txn[int(txnId) - 1].read_set.append(dataAffected) # Adding read_set
                elif(txnType == 'W'):
                    txn[int(txnId) - 1].write_set.append(dataAffected) # Adding write_set
                    
    start_time = time.time()
    for val in txnSequence:
        txnType, txnId, dataAffected = Util.parseTxnElmt(val)
        if(txnType in ['R', 'W']):
            # * Read phase
            if(txn[txnId - 1].START is None):
                txnStart = round(time.time() - start_time, 2)
                txn[txnId - 1].START = txnStart
                print(f"[READ PHASE T{txnId}] Starting read phase in transaction {txnId} in t={txn[txnId-1].START}")
            isRead = True if txnType == 'R' else False
            read(dataAffected, isRead, txnId)
            time.sleep(1)
        elif(txnType == 'C'):
            # * Validation
            validated = False
            txn[txnId - 1].TS = round(time.time() - start_time, 2)
            print(f"[VALIDATION PHASE T{txnId}] Starting validation of transaction {txnId}")
            if(not(validatedTxnId)): # If it is the first transaction commited
                validated = True
                
            for val in (validatedTxnId):
                if(txn[val - 1].TS < txn[txnId - 1].TS):
                    firstCondition = txn[val - 1].FINISH < txn[txnId - 1].START
                    isDisjoint = not(bool(set(txn[txnId - 1].read_set) & set(txn[val - 1].write_set)))
                    secondCondition = (txn[val - 1].FINISH < txn[txnId - 1].TS) and isDisjoint
                    if(firstCondition or secondCondition):
                        validated = True
            time.sleep(1)
            
            # * Write phase
            # printTxnsTimestamp(txn) // # ! For debug
            
            if(validated):
                print(f"[VALIDATION PHASE T{txnId}] Finish validating of T{txnId}")
            else: # * Exit failed case
                print(f"[VALIDATION PHASE T{txnId}] Failed to validating T{txnId}")
                exit()
            
            print(f"[WRITE PHASE T{txnId}] Applied transaction T{txnId} updates to the database")
            txn[txnId - 1].FINISH = round(time.time() - start_time, 2)
            validatedTxnId.append(txnId)
            time.sleep(1)
            
            # * Exit success case
            if(len(validatedTxnId) == numTxn):
                print("[!!!! FINISHED !!!!] All transaction is validated")
                exit()
        else:
            print("[Corner case] unwanted data item")