import threading

class BankAccount:
    def __init__(self, balance):
        self.balance = balance
        self.lock = threading.Lock()  # Create a lock

    def withdraw(self, amount):
        with self.lock:  # Acquire the lock
            if self.balance >= amount:
                # Simulate processing time (where a race would occur without the lock)
                import time
                time.sleep(0.1)
                self.balance -= amount
                print(f"Withdrew {amount}. New balance: {self.balance}")
                return True
            else:
                print("Insufficient funds")
                return False

# Both threads will now access the account safely, one after the other.
account = BankAccount(1000)
thread1 = threading.Thread(target=account.withdraw, args=(800,))
thread2 = threading.Thread(target=account.withdraw, args=(500,))
thread1.start()
thread2.start()   