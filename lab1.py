import psycopg2
import threading
import time
from connect_lab1 import get_connection

#Очищення
def reset_counter():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE user_counter SET counter = 0, version = 0 WHERE user_id = 1")
    conn.commit()
    cur.close()
    conn.close()

#Результат
def get_final_value():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT counter FROM user_counter WHERE user_id = 1")
    val = cur.fetchone()[0]
    cur.close()
    conn.close()
    return val

#LOST UPDATE
def lost_update_thread():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(10_000):
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1")
        counter = cur.fetchone()[0]
        counter += 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        conn.commit()
    cur.close()
    conn.close()

def run_lost_update():
    print("\nLost Update")
    reset_counter()
    threads = []
    start = time.time()
    for _ in range(10):
        t = threading.Thread(target=lost_update_thread)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    print(f"Час: {end - start:.2f} c")
    print(f"Counter: {get_final_value()}")


#IN-PLACE UPDATE
def inplace_update_thread():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(10_000):
        cur.execute("UPDATE user_counter SET counter = counter + 1 WHERE user_id = 1")
        conn.commit()
    cur.close()
    conn.close()

def run_inplace_update():
    print("\nIn-Place Update")
    reset_counter()
    threads = []
    start = time.time()
    for _ in range(10):
        t = threading.Thread(target=inplace_update_thread)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    print(f"Час: {end - start:.2f} c")
    print(f"Counter: {get_final_value()}")


#ROW-LEVEL LOCKING
def row_locking_thread():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(10_000):
        cur.execute("BEGIN")
        cur.execute("SELECT counter FROM user_counter WHERE user_id = 1 FOR UPDATE") #SELECT ... FOR UPDATE блокує рядок user_id = 1
        counter = cur.fetchone()[0] + 1
        cur.execute("UPDATE user_counter SET counter = %s WHERE user_id = 1", (counter,))
        conn.commit()
    cur.close()
    conn.close()

def run_row_locking():
    print("\nRow-Level Locking")
    reset_counter()
    threads = []
    start = time.time()
    for _ in range(10):
        t = threading.Thread(target=row_locking_thread)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    print(f"Час: {end - start:.2f} c")
    print(f"Counter: {get_final_value()}")


#OPTIMISTIC CONCURRENCY
def optimistic_thread():
    conn = get_connection()
    cur = conn.cursor()
    for _ in range(10_000):
        while True:
            cur.execute("SELECT counter, version FROM user_counter WHERE user_id = 1")
            counter, version = cur.fetchone()
            counter += 1
            cur.execute(
                "UPDATE user_counter SET counter = %s, version = %s WHERE user_id = 1 AND version = %s",
                (counter, version + 1, version)
            )
            conn.commit()
            if cur.rowcount > 0:
                break
    cur.close()
    conn.close()

def run_optimistic():
    print("\Optimistic Concurrency")
    reset_counter()
    threads = []
    start = time.time()
    for _ in range(10):
        t = threading.Thread(target=optimistic_thread)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    end = time.time()
    print(f"Час: {end - start:.2f} c")
    print(f"Counter: {get_final_value()}")

if __name__ == "__main__":
    #run_lost_update()
    #run_inplace_update()
    #run_row_locking()
    run_optimistic()
