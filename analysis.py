#!/bin/python3
# -*- coding: utf-8 -*-

import json
import r2pipe
import hashlib
import sqlite3 as sql
import time
import sys


def get_bblocks(object):
    return object.get('BasicBlocks')

def count():
    output = []
    for file in result:
        bb = 0
        fn = 0
        for i in result[file]:
            try:
                i['Block_SHA256']
            except KeyError:
                fn += 1
            else:
                bb += 1
        output.append({"File": file, "BasicBlocks": bb, "Functions": fn})
    output.sort(key=get_bblocks, reverse=True)
    print(output)


def analysis(data, a):
    if a == 0:
        cr.execute("Select * FROM Functions WHERE Func_SHA256 = ?", (data,))
        for f in cr:
            try:
                result[f[0]]
            except KeyError:
                result[f[0]] = []
                result[f[0]].append({
                    'Func_SHA256': f[1]
                })
            else:
                result[f[0]].append({
                    'Func_SHA256': f[1]
                }) 

    elif a == 1:
        cr.execute("Select * FROM Blocks WHERE Block_SHA256 = ?", (data,))
        for b in cr:
            try:
                result[b[0]]
            except KeyError:
                result[b[0]] = []
                result[b[0]].append({
                    'Block_SHA256': b[1]
                })
            else:
                result[b[0]].append({
                    'Block_SHA256': b[1]
                })


def extract_func(file):
    uniq_hashes = []
    r2 = r2pipe.open(file)
    r2.cmd("aaaa")
    function_list = r2.cmdj("aflj")
    counter = 1
    while function_list is None:
        time.sleep(0.7)
        function_list = r2.cmdj("aflj")
        counter += 1
        if counter > 10:
            print("exit")
            sys.exit()

    for function in function_list:
        try:
            op_string = r2.cmd("p8f" + str(function["size"])+ " @ " + function["name"])
            op = op_string[:-1]
            op = op.encode('utf-8')
            op_hash = hashlib.sha256(op).hexdigest()
            if op_hash not in uniq_hashes:
                analysis(op_hash, 0)
                uniq_hashes.append(op_hash)
        except:
            print("exit")
            sys.exit()
    r2.quit()



def extract_bblock(file):
    r2 = r2pipe.open(file)
    r2.cmd("aaaa")
    uniq_hashes = []
    blocks_data = r2.cmd('pdbj @@ *')
    counter = 1
    while blocks_data == '':
        time.sleep(0.7)
        blocks_data = r2.cmd('pdbj @@ *')
        counter += 1
        if counter > 10:
            print("exit")
            sys.exit()

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
                analysis(code_hash, 1)                 
                uniq_hashes.append(code_hash)

        except:
            print("exit")
            sys.exit()
    r2.quit()


def main():
    FILE = sys.argv[1]

    extract_func(FILE)
    extract_bblock(FILE)

    count()

    #fd = open('result', 'w', encoding='utf-8')
    #json.dump(result, fd, ensure_ascii=False, indent=4)
    #fd.close()



if __name__ == '__main__':
    result = {}

    db = sql.connect('dataset.db')
    cr = db.cursor()

    main()

    db.close()
