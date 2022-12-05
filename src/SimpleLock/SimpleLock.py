import Util
import copy

class Operation:

    def __init__(self, SLTransaction, action, SLData, lockManager):
        self.SLTransaction = SLTransaction
        self.action = action
        self.SLData = SLData 
        self.lockManager = lockManager
    
    def run(self):
        if (self.SLTransaction.transaction.id in self.lockManager.deadlocked_transactions):
            self.lockManager.deadlocked_operation.append(self)
        else:
            success = True
            if (self.action == 'R'):
                success = self.SLTransaction.read(self.SLData)
            elif (self.action == 'W'):
                success = self.SLTransaction.write(self.SLData)
            else:
                success = self.SLTransaction.commit()
            if (not success):
                self.lockManager.pending.append(self)
                if (not isinstance(self.SLData, str) and len(self.SLData.lock) > 0):
                    wait_id = self.SLTransaction.transaction.id
                    waitee_id = self.SLData.lock[0]
                    deadlock = self.lockManager.search_deadlock(wait_id, waitee_id)
                    if not deadlock:
                        self.lockManager.deadlock_detector[waitee_id].append(wait_id)
                    else:
                        if (wait_id > waitee_id):
                            del_id = wait_id
                        else:
                            del_id = waitee_id
                        print(f'\n!!! ABORTING T{del_id} BECAUSE A DEADLOCK HAS BEEN DETECTED!!!\n'.format(del_id))
                        self.lockManager.delete_lock(del_id)
                        self.lockManager.deadlocked_transactions.append(del_id)
                        length = len(self.lockManager.pending)
                        for i in range(length):
                            operation = self.lockManager.pending.pop(0) 
                            operation.run()

class Transaction:
    
    def __init__(self, id):
        self.id = id

class Data:

    def __init__(self, label):
        self.label = label

class LockManager:

    def __init__(self, all_data):
        self.all_data = all_data
        self.pending = []
        self.deadlock_detector = {}
        self.deadlocked_transactions = []
        self.deadlocked_operation = []

    def exclusive_lock(self, transaction, data):
        if (transaction.transaction.id not in self.deadlock_detector):
            self.deadlock_detector[transaction.transaction.id] = []
        if ((len(data.lock) > 0) and (transaction.transaction.id == data.lock[0])):
            return True
        success = True
        for operation in self.pending:
            if (operation.SLTransaction.transaction.id == transaction.transaction.id):
                success = False 
                break
        if (success):
            data.lock.append(transaction.transaction.id)
            if (transaction.transaction.id != data.lock[0]):
                self.deadlock_detector[data.lock[0]].append(transaction.transaction.id)
                success = False
        return success
    
    def search_deadlock(self, wait_id, wait_id2):
        wait1 = False
        wait2 = False
        if wait_id2 in self.deadlock_detector:
            if wait_id in self.deadlock_detector[wait_id2]:
                wait1 = True
        if wait_id in self.deadlock_detector:
            if wait_id2 in self.deadlock_detector[wait_id]:
                wait2 = True

        return wait1 and wait2

    def delete_lock(self, transaction_id):
        for data in self.all_data:
            if transaction_id in data.lock:
                data.lock.remove(transaction_id)
        self.deadlock_detector.pop(transaction_id, None)

class SLTransaction:

    def __init__(self, transaction, lockManager):
        self.transaction = transaction
        self.lockManager = lockManager
    
    def write(self, SLData):
        success = self.lockManager.exclusive_lock(self, SLData)
        if (success):
            print(f'W{self.transaction.id}({SLData.data.label})')
            return True
        else:
            print(f'W{self.transaction.id}({SLData.data.label}) is waiting')
            return False

    def read(self, SLData):       
        success = self.lockManager.exclusive_lock(self, SLData)
        if (success):
            print(f'R{self.transaction.id}({SLData.data.label})')
            return True
        else:
            print(f'R{self.transaction.id}({SLData.data.label}) is waiting')
            return False


    def commit(self):
        success = True
        for operation in self.lockManager.pending:
            if (operation.SLTransaction.transaction.id == self.transaction.id):
                success = False
                break
        
        if (success):
            for index, data in enumerate(self.lockManager.all_data):
                if (len(data.lock) > 0 and data.granted_lock() == self.transaction.id):
                    data_pop = data.lock.pop(0)
            self.lockManager.deadlock_detector.pop(self.transaction.id, None)
            print(f'C{self.transaction.id}')
            
            length = len(self.lockManager.pending)
            for i in range(length):
                operation = self.lockManager.pending.pop(0) 
                operation.run()
        else:
            print(f'C{self.transaction.id} is waiting')
        return success

class SLData:

    def __init__(self, data):
        self.data = data
        self.lock = []
    
    def granted_lock(self):
        return self.lock[0]


def run_SL(filename):
    print('Menghitung Metode Simple Locking')
    T, data, operation_string = Util.generalSetup(filename)
    arrOperation, lockManager = Util.SLock_Converter(T, data, operation_string)

    for operation in arrOperation:
        operation.run()

    lockManager.deadlocked_transactions = []

    newArrOperation = copy.deepcopy(lockManager.deadlocked_operation)
    lockManager.deadlocked_operation = []

    while (len(newArrOperation) > 0):
        print('Retry Aborted Transactions')
        for operation in newArrOperation:
            operation.run()
        lockManager.deadlocked_transactions = []
        newArrOperation = copy.deepcopy(lockManager.deadlocked_operation)
        lockManager.deadlocked_operation = []

    if len(lockManager.deadlocked_transactions) > 0:
        print('\nTransactions:')
        for deadlock in lockManager.deadlocked_transactions:
            print(f'T{deadlock}'.format(deadlock))  