#遗传算法（Genetic Algorithm）实现
import math
import numpy as np
import pandas as pd
import random
#全局变量
pop_size = 1000#种群个体数
chromosome_len = 17#染色体长度
pop = []#种群
x = []#自变量
fit_value = []#适度值
pc = 0.6#交叉概率
pm = 0.1#变异概率
def init():
    #初始化种群
    pop = np.random.randint(0,2,[pop_size,chromosome_len])#生成种群
    return pop
def get_chomo_str(pop):
    #获得字符串形式的二进制编码
    res = []
    for i in range(pop_size):
        chromosome_str = [str(i) for i in pop[i]]#把整数列表转换成字符串
        chromosome_str = "".join(chromosome_str)#拼接成字符串
        res.append(chromosome_str)
    return res
def decodechrom(chromosome,lower_bound,upper_bound):
    #解码染色体
    chromosome_str = [str(i) for i in chromosome]#把整数列表转换成字符串
    chromosome_str = "".join(chromosome_str)#拼接成字符串
    dec = int(chromosome_str,2)#转换成十进制
    return lower_bound + dec/(2**len(chromosome)-1)*(upper_bound-lower_bound)
def decode(pop):
    #解码种群
    x = []
    for i in range(pop_size):
        x.append(decodechrom(pop[i],0,9))
    return x
def eval(x):
    #计算适度值
    return x + 10*math.sin(5*x) + 7*math.cos(4*x)
def get_fit_value(x):
    #获得种群适度值
    fit_value = []
    for i in range(pop_size):
        fit_value.append(eval(x[i]))
    return fit_value
def cum_p(tab):
    #计算累积概率
    t = 0
    for i in range(tab.shape[0]):
        t = t + tab.loc[i,"p"]
        tab.loc[i,"cum_p"] = t
    return tab
def select(tab):
    #选择【轮盘赌选择】
    fit_value_sum = tab['fit_value'].sum()
    tab['p'] = tab['fit_value']/fit_value_sum#个体选择概率
    tab = cum_p(tab)#获得累积概率
    for index,row in tab.iterrows():
        rand = random.random()#[0,1)之间的随机浮点数
        if row['cum_p'] < rand:
            tab = tab.drop(index)
    tab = tab.reset_index(drop=True)
    tab = tab.drop(['p','cum_p'],axis=1)
    return tab
def get_child(father,mother,copint,type):
    if type == "son":
        father[copint:] = 0
        mother[:copint] = 0
    elif type == "daughter":
        father[:copint] = 0
        mother[copint:] = 0
    return father + mother
def cross(pop,half):
    #交叉
    #half为拆半后的个体数
    father = pop[:half]
    mother = pop[half:]
    np.random.shuffle(father)
    np.random.shuffle(mother)
    res = []
    for i in range(half):
        if np.random.uniform(0,1)<=pc:
            copint = np.random.randint(0,int(father.shape[0]/2))#交换基因的位置
            son = get_child(father[i],mother[i],copint,type="son")
            daughter = get_child(father[i],mother[i],copint,type="daughter")
        else:
            son = father[i]
            daughter = mother[i]
        res.append(son)
        res.append(daughter)
    return res
def mutate(pop):
    #变异
    for i in range(pop.shape[0]):
        if np.random.uniform(0,1) <= pm:
            #变异
            position = np.random.randint(0,len(pop[i]))
            if pop[i][position] == 1:
                pop[i][position] = 0
            else:
                pop[i][position] = 1
    return pop
pop = init()#初始化种群

for k in range(20):
    print("第%d次迭代"%(k+1))
    print(pop)
    x = decode(pop)#解码
    fit_value = get_fit_value(x)#获得适度值
    pop_tab = pd.DataFrame({"chomosome":get_chomo_str(pop),"x":x,"fit_value":fit_value})#构造表
    pop_tab = pop_tab.drop(pop_tab[pop_tab['fit_value']<0].index)
    pop_tab = pop_tab.sort_values(["fit_value"]).reset_index(drop=True)#根据适度值进行排序
    print("此时最优个体为：%s\n自变量x=%lf\n适度值为：%lf"%(pop_tab.iloc[-1,:]["chomosome"],pop_tab.iloc[-1,:]['x'],pop_tab.iloc[-1,:]['fit_value']))
    #print(pop_tab.iloc[-1,:]["chomosome"])
    pop_tab = select(pop_tab)
    half = int(pop_tab.shape[0]/2)
    if half <= 1:
        break
    pop = []
    for i in pop_tab['chomosome'].to_list():
        tmp = [int(char) for char in i]
        pop.append(tmp)
    pop = np.array(pop)#得到保留下的种群

    #print("选择后",pop)
    pop = np.array(cross(pop,half))#交叉产生后代
    # print("交叉后",pop)
    pop = mutate(pop)#变异
    # print("变异后",pop)
    pop_size = pop.shape[0]