# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 20:20:38 2021

@author: 张铁柱
"""
def RTSim(seriesA, seriesB):
    #RamType
    if 'x_ram_type' in seriesA.keys() and 'x_ram_type' in seriesB.keys():
            if (seriesA['x_ram_type'] not in seriesB['x_ram_type']) and (seriesB['x_ram_type'] not in seriesA['x_ram_type']):
                return False

    return True

def CMSim(seriesA, seriesB):
    #CpuModel
    for colVeto in ('x_cpu_model',):
        if (
            colVeto in  seriesA.keys() and
            colVeto in  seriesB.keys() and
            ((seriesA[colVeto]  not in seriesB[colVeto]) or (seriesB[colVeto] not in seriesA[colVeto]))
        ):
            return False
    return True

def RCSim(seriesA, seriesB):
    #RamCapacity
    if (
        'x_ram_capacity' in seriesA.keys() and
        'x_ram_capacity' in seriesB.keys() and
        not (
            'x_model' in seriesA.keys() and seriesA['x_model'].startswith('x220 429') and
            'x_model' in seriesB.keys() and seriesB['x_model'].startswith('x220 429')
        ) and
        seriesA['x_ram_capacity'] != seriesB['x_ram_capacity']
    ):
        return False

    return True

def MSim(seriesA, seriesB):
    #Model
    for colVeto in ('x_model',):
        if (
            colVeto in  seriesA.keys() and
            colVeto in  seriesB.keys() and
            ((seriesA[colVeto] in seriesB[colVeto]) or (seriesB[colVeto] in seriesA[colVeto]))
        ):
            return True
    return False

def CBSim(seriesA, seriesB):
    #CpuBrand
    for colVeto in ('x_cpu_brand',):
        if (
            colVeto in  seriesA.keys() and
            colVeto in  seriesB.keys() and
            seriesA[colVeto] != seriesB[colVeto]
        ):
            return False
    return True

def CFSim(seriesA, seriesB):
    #CpuFrequency
    for colVeto in ('x_cpu_frequency',):
        if (
            colVeto in  seriesA.keys() and
            colVeto in  seriesB.keys() and
            seriesA[colVeto] != seriesB[colVeto]
        ):
            return False
    return True

def SiSim(seriesA, seriesB):
    #Size
    for colVeto in ('x_size',):
        if (
            colVeto in  seriesA.keys() and
            colVeto in  seriesB.keys() and
            seriesA[colVeto] != seriesB[colVeto]
        ):
            return False
    return True

def SSDSim(seriesA, seriesB):
    #SSD capacity
    if (
            'x_ssd_capacity' in  seriesA.keys() and
            'x_ssd_capacity' in  seriesB.keys() and
            # seriesA['x_ssd_capacity'] != 0 and
            # seriesB['x_ssd_capacity'] != 0 and
            seriesA['x_ssd_capacity'] != seriesB['x_ssd_capacity']
        ):
            return False
    return True

def HDDSim(seriesA, seriesB):
    #HDD capacity
    if (
            'x_hdd_capacity' in  seriesA.keys() and
            'x_hdd_capacity' in  seriesB.keys() and
            seriesA['x_hdd_capacity'] != 0 and
            seriesB['x_hdd_capacity'] != 0 and
            seriesA['x_hdd_capacity'] != seriesB['x_hdd_capacity']
        ):
            return False
    return True

def ProdSim(seriesA, seriesB):
    #判断是否相等
    if RTSim(seriesA, seriesB) and CBSim(seriesA, seriesB) :
        # if not SSDSim(seriesA, seriesB):
        #     return False
        # if not HDDSim(seriesA, seriesB):
        #     return False
        if not MSim(seriesA, seriesB):
            return False
        if CMSim(seriesA, seriesB) and RCSim(seriesA, seriesB) :#and CFSim(seriesA, seriesB): #加了CF的比较，自测下降了...
            return True
    return False



def Clustering(products, blocks):
    product_address, product_set = dict(), dict()
    unpsb = set()

    cluster_num, unpsb_num = 1, 0
    for block in sorted(list(blocks.values()),reverse=False):
        block = block.split(',')
        for k1 in range(len(block)):
            product_a_id = block[k1]
            for k2 in range(k1 + 1, len(block)):
                product_b_id = block[k2]

                if (product_a_id, product_b_id) in unpsb:
                        unpsb_num += 1
                        continue

                if not product_address.__contains__(product_a_id):
                    if not product_address.__contains__(product_b_id):
                        # product a not belongs to a class,and product b not belongs to a class

                        #print(products.get(product_a_id),products.get(product_b_id))
                        if ProdSim(products.get(product_a_id), products.get(product_b_id)):

                            product_address[product_a_id] = cluster_num
                            product_address[product_b_id] = cluster_num
                            product_set[cluster_num] = set(
                                [product_a_id, product_b_id])
                            cluster_num += 1
                        else:
                            unpsb.add((product_a_id, product_b_id))
                    else:
                        # product a not belongs to a class,but product b belongs to a class
                        if ProdSim(products.get(product_a_id), products.get(product_b_id)):
                            product_address[product_a_id] = product_address[product_b_id]
                            product_set[product_address[product_b_id]].add(
                                product_a_id)
                        else:
                            unpsb.add((product_a_id, product_b_id))
                else:
                    if not product_address.__contains__(product_b_id):
                        # product a belongs to a class,but product b not belongs to a class
                        if ProdSim(products.get(product_a_id), products.get(product_b_id)):
                            product_address[product_b_id] = product_address[product_a_id]
                            product_set[product_address[product_a_id]].add(
                                product_b_id)
                        else:
                            unpsb.add((product_a_id, product_b_id))
                    else:
                        # product a belongs to a class,and product b belongs to another class
                        a_address, b_address = product_address[product_a_id], product_address[product_b_id]
                        if a_address != b_address:
                            if ProdSim(products.get(product_a_id), products.get(product_b_id)):
                                for product_id in product_set[b_address]:
                                    product_address[product_id] = product_address[product_a_id]
                                product_set[a_address] = product_set[a_address].union(
                                    product_set[b_address])
                                del[product_set[b_address]]
                                cluster_num += 1
                            else:
                                unpsb.add((product_a_id, product_b_id))

    return (product_set,unpsb)
