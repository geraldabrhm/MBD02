import SimpleLock as SL

class Transaction:

    def __init__(self, id):
        self.id = id

    def __str__(self):
        return 'T' + str(self.id)
    
    def __eq__(self, transaction):
        return (self.id == transaction.id)
            

class Operation:

    def __init__ (self, transaction=None, action=None, data=None, operation=None):
        if (operation):
            self.transaction = operation.transaction
            self.action = operation.action
            self.data = operation.data
        else:
            self.transaction = transaction
            self.action = action
            self.data = data
    
    def __str__(self):
        data = f'({self.data})' if (self.action == 'R' or self.action == 'W') else ""
        return f'{self.action}{self.transaction.id}{data}'

# Membaca File
def generalSetup(fileName):
    file = open("./fileInput/" + fileName, "r")
    buff = file.read()
    arrString = buff.split('\n')
    arrTransaction = []
    num_of_transaction = int(arrString.pop(0))
    for i in range(num_of_transaction):
        arrTransaction.append(Transaction(i+1))
    raw_data = arrString.pop(0).split(' ')
    arrOperation = []
    for s in arrString:
        s = s.replace('(', '')
        s = s.replace(')', '')
        if len(s) > 2:
            arrOperation.append(
                Operation(
                    arrTransaction[int(s[1])-1],
                    s[0],
                    s[2]
                )
            )
        else:
            arrOperation.append(
                Operation(
                    arrTransaction[int(s[1])-1],
                    s[0]
                )
            )

    return arrTransaction, arrOperation, raw_data

def SLock_Converter(arrTransaction, arrData, arrString):
    SL_DataContainer = []
    arrDataLabel = []
    for data in arrData:
        data_label = data.data
        arrDataLabel.append(data_label)
        SL_DataContainer.append(SL.SLData(SL.Data(data_label)))
    SL_LockManager = SL.LockManager(SL_DataContainer)
    arrSLTransaction = []
    for transaction in arrTransaction:
        arrSLTransaction.append(SL.SLTransaction(transaction, SL_LockManager))
    arrOperation = []
    for proc in arrData:
        transaction_id = proc.transaction.id
        action = proc.action
        dataLabel = proc.data
        arrOperation.append(SL.Operation(arrSLTransaction[transaction_id - 1], action, SL_DataContainer[arrDataLabel.index(dataLabel)], SL_LockManager))

    return arrOperation, SL_LockManager