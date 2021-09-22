#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import r2pipe
import hashlib
import sqlite3 as sql
import multiprocessing
import time
import sys, os


def extract_func(file):
    uniq_hashes = []
    r2 = r2pipe.open(path+file)
    r2.cmd("aaaa")
    function_list = r2.cmdj("aflj")
    while function_list is None:
        time.sleep(0.7)
        function_list = r2.cmdj("aflj")

    for function in function_list:
        try:
            op_string = r2.cmd("p8f" + str(function["size"])+ " @ " + function["name"])   
            op = op_string[:-1]

            op = op.encode('utf-8')
            op_hash = hashlib.sha256(op).hexdigest()
            if op_hash not in uniq_hashes:
                cr.execute("""INSERT INTO Functions 
                    VALUES (?, ?)""", (file, op_hash))
                db.commit()
                uniq_hashes.append(op_hash)
        except:
            cr.execute("""INSERT INTO error_func 
                VALUES (?, ?)""", (file, str(function["name"])))
            db.commit()
    r2.quit()


def extract_bblock(file):
    r2 = r2pipe.open(path+file)
    r2.cmd("aaaa")
    uniq_hashes = []
    blocks_data = r2.cmd('pdbj @@ *')
    while blocks_data == '':
        time.sleep(0.7)
        blocks_data = r2.cmd('pdbj @@ *')

    blocks_data = blocks_data.split('\n')
    blocks_data.remove('')

    blocks = set()
    for bb in blocks_data:
            blocks.add(bb)
    blocks = list(blocks)
    for block in blocks:
        try:
            block = json.loads(block)
            code = b''
            for b in block:
                if b['type'] != 'invalid':
                    code += bytes.fromhex(b['bytes'])
            code_hash = hashlib.sha256(code).hexdigest()

            if code_hash not in uniq_hashes:
                cr.execute("""INSERT INTO Blocks 
                    VALUES (?, ?)""", (file, code_hash))  
                db.commit()
                uniq_hashes.append(code_hash)
        except:
            cr.execute("""INSERT INTO error_block 
                VALUES (?, ?)""", (file, str(block)))
            db.commit()

    r2.quit()


def main():

    FILES = os.listdir(path)

    for file in FILES:
        p = multiprocessing.Process(target=extract_func, args=(file,))
        p.start()
        p.join(30)
        if p.is_alive():
            p.kill()
            cr.execute("""INSERT INTO error_func_timeout 
                VALUES (?)""", (file,))
            db.commit()
            p.join()


        p2 = multiprocessing.Process(target=extract_bblock, args=(file,))
        p2.start()
        p2.join(40)
        if p2.is_alive():
            p2.kill()
            cr.execute("""INSERT INTO error_block_timeout 
                VALUES (?)""", (file,))
            db.commit()
            p2.join()
            

    

if __name__ == '__main__':
    path = sys.argv[1]
    db = sql.connect('/home/io/umay/tools/db/final_1030_new.db')
    cr = db.cursor()
    cr.execute("CREATE TABLE Functions (File, Func_SHA256)")
    cr.execute("CREATE TABLE Blocks (File, Block_SHA256)")
    cr.execute("CREATE TABLE error_block (File, Block)")
    cr.execute("CREATE TABLE error_block_timeout (File)")
    cr.execute("CREATE TABLE error_func (File, Func_name)")
    cr.execute("CREATE TABLE error_func_timeout (File)")
    db.commit()

    main()
    
    db.close()