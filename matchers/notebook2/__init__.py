# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 17:26:26 2021

@author: 张铁柱
"""
import pandas as pd
import typing
from . import extract
from . import cluster
from .. import AbstractMatcher
from .. import timing
from tqdm import tqdm
import itertools
import re

def getEqualModelName(model: str) -> str:
    for g in (
        {'x220 4287', 'x220 4290', 'x220 4291'},
        {'x130 2338', 'x130 2339'},
        {'x130 0622', 'x130 0627'},
        {'x230 2320', 'x230 3435'},
        {'v7-482', 'v7-582'},
        {'i5547-3751slv', 'i5547-3753slv'},
    ):
        if model in g:
            return tuple(g)[0]
    return model

class matcher(AbstractMatcher):
    @staticmethod
    def check(df: pd.DataFrame) -> bool:
        if all(
            col in df.columns
            for col in (
                'instance_id',
                'brand',
                'cpu_brand',
                'cpu_model',
                'cpu_type',
                'cpu_frequency',
                'ram_capacity',
                'ram_type',
                'ram_frequency',
                'hdd_capacity',
                'ssd_capacity',
                'weight',
                'dimensions',
                'title',
            )
        ) and df.iloc[1].at['instance_id'].startswith('source'):  #匹配X3,它的id是以source开头的
                return True
        return False

    @staticmethod
    @timing('Extract')
    def extract(df: pd.DataFrame) -> None:
        # 将所有数据转为小写
        for col in df.columns:
            df[col] = df[col].str.lower()
        # 通过正则表达式解析信息
        df['x_brand'] = df.apply(extract.brand, axis=1)
        df['x_weight'] = df.apply(extract.weight, axis=1)
        df[['x_hdd_capacity', 'x_ssd_capacity']] = df.apply(extract.diskCapacity, axis=1)
        df['x_cpu_brand'] = df.apply(extract.cpuBrand, axis=1)
        df['x_cpu_model'] = df.apply(extract.cpuModel,axis=1)
        df['x_cpu_frequency'] = df.apply(extract.cpuFrequency, axis=1)
        df['x_ram_capacity'] = df.apply(extract.ramCapacity, axis=1)
        df['x_ram_type'] = df.apply(extract.ramType, axis=1)
        df['x_win_type'] = df.apply(extract.winType, axis=1)
        df['x_model'] = df.apply(extract.model, axis=1)
        df['x_model'] = df['x_model'].apply(getEqualModelName)
        df['x_size'] = df.apply(extract.size, axis=1)
    
    @staticmethod
    @timing('MatchBrand')
    def MatchBrand(df: pd.DataFrame):
        brands,pds_with_bds, pds_without_bds=['other'],{},{}
        '''
        pds_with_bds={brand1:{id1:{description},id2:{description},...},...}
        
        '''
        
        for i in range(df.shape[0]):
            nk=df.iloc[i]
            if(not pd.isna(nk['x_brand'])):
                if nk['x_brand'] not in brands:
                    brands.append(nk['x_brand'])
                
                if nk['x_brand'] not in pds_with_bds.keys():
                    pds_with_bds[nk['x_brand']]=dict()
                
                pds_with_bds[nk['x_brand']][nk['instance_id']]=dict()
                #描述属性暂时只保留这6个
                for pkey in ['x_ram_type','x_model','x_cpu_brand','x_cpu_model','x_cpu_frequency','x_ram_capacity']:
                    if not pd.isna(nk[pkey]):
                        pds_with_bds[nk['x_brand']][nk['instance_id']][pkey]=nk[pkey]
            
            else:
                pds_without_bds[nk['instance_id']]=dict()
                for pkey in ['x_ram_type','x_model','x_cpu_brand','x_cpu_model','x_cpu_frequency','x_ram_capacity']:
                    if not pd.isna(nk[pkey]):
                        pds_without_bds[nk['instance_id']][pkey]=nk[pkey]
        
        return (brands,pds_with_bds, pds_without_bds)
    
    def Transfer(tokens, k):
        result = []
        if tokens:
            filter(None, tokens) #过滤掉None
            if(len(tokens) >= k):
                for i in itertools.combinations(tokens, k):
                    i = list(i)
                    result.append(tuple(i))
        return result
    
    @classmethod
    @timing('BlockScheme')  
    def Block_Scheme(cls,dataset, tokenizer, transfer):
        """
            input:  dataset ;
            tokenizer :  "mw" ;
            transfer : integer k
            output: a dictionary : key-value: ('word1','word2',...,'wordk'):"product_id1,product_id2,..."
        """
        blocks = {}
        if dataset:
            for product_id, profile in sorted(dataset.items(), key=lambda x: x[0]):
                dict_d = dict(profile)
                description = list(dict_d.values())
                temblocks = cls.Transfer(description, transfer)
    
                for block in temblocks:
                    if block not in blocks:
                        blocks[block] = [product_id]
                    else:
                        blocks[block].append(product_id)
    
        new_blocks = {}
        for k in list(blocks.keys()):
            if len(blocks[k]) >= 2:
                new_blocks[k] = ','.join(sorted(blocks[k]))
        del blocks
        return new_blocks
    
    def IDEqual(df,seriesA,seriesB):
        #有些Other Laptops & Notebooks，可以直接判断title里的id
        t1=df.iloc[seriesA].at['title']
        t2=df.iloc[seriesB].at['title']
        if ("id:" in t1) and ("id:" in t2):
            id1=re.search(re.compile(r'\b(id:)(\d+)\b'),str(t1))
            id2=re.search(re.compile(r'\b(id:)(\d+)\b'),str(t2))
            if not pd.isna(id1) and not pd.isna(id2) :
                if id1.group()!=id2.group():
                    return False
        return True
    
    @classmethod
    @timing('Match')              
    def match(cls, df: pd.DataFrame) -> typing.Iterable[typing.Tuple[str, str]]:
        
        # match the brand
        brands, pds_with_bds, pds_without_bds = cls.MatchBrand(df)
        pds_with_bds['unknown'] = pds_without_bds
        
        # process each brand class
        results = []
        for brand in tqdm(sorted(list(pds_with_bds.keys()))):
            product = pds_with_bds[brand]
            
            if len(product.keys()) < 2:
                continue
    
            # block scheme 
            blocks = cls.Block_Scheme(product, 'mw', 1)  #k可变
            
            # clustering
            product_set,unpsb = cluster.Clustering(product, blocks)  #unpsb保存不相等的id pairs
            
            # add record
            for clus in product_set.values():
                if len(clus) < 2:
                    continue
                for pair in itertools.combinations(clus, 2):
                    id_a, id_b = pair
                    
                    if not cls.IDEqual(df,df[df['instance_id']==id_a].index.tolist()[0],df[df['instance_id']==id_b].index.tolist()[0]):
                        unpsb.add((id_a,id_b))
                        continue
                        
                    if (id_a,id_b) in unpsb:
                        continue
                    
                    results.append((id_a, id_b))
        return results
