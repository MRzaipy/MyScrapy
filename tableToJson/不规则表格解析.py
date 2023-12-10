from lxml import etree


class threeTier():
    def __init__(self, verticalData):
        self.verticalData = verticalData  # 竖型排序的数据
        self.dic = {}  # 最终返回的数据
        self.Rank = {}  # 存储  子数据与父数据   子：key : 父：value  便于知道该当前数据是否拥有 父亲
        self.record = {}  # 存储已处理的数据，防止重复处理
        self.Hindex = {"其他t": 2}  # 解析演示表格三你就知道了

    def StringOperate(self, str):
        return "".join("".join(str).split(" ")).replace("\n", "").replace("\r", "").replace("\t", "").replace("\xa0", "").strip()

    def tdHandle(self,td):
        content = self.StringOperate(td.xpath(".//text()"))
        return content

    def firstAnalysis(self, table):
        trs = table.xpath(".//tr")
        rowSpanIndex = []
        data = []

        for tr in range(len(trs)):
            taks = []
            for td in trs[tr]:
                rowspan = self.StringOperate(td.xpath("./@rowspan"))
                if rowspan and int(rowspan) > 1:
                    title = self.tdHandle(td)
                    rowspan = int(rowspan)
                    rowSpanIndex.append([title, tr, rowspan])
                v = self.tdHandle(td)
                if v != '万元':
                    taks.append(v)
            data.append(taks)

        titles = []
        s = []

        for n in range(len(rowSpanIndex)-1, -1, -1):
            itme = rowSpanIndex[n]
            title = itme[0]
            sIndex = itme[1]
            eIndex = itme[1] + itme[2]
            titles.append(title)
            s.insert(0, eIndex)
            for d in data[sIndex:eIndex]:
                if len(d) == 1 and title in d:
                    data.remove(d)
                elif title not in d:
                    d.insert(0, title)

        for i in range(len(s)):
            if i+1 == len(s):
                break
            ttt = s[i+1:]
            r = rowSpanIndex[i+1:]
            for n in range(len(ttt)):
                S = s[i]
                T = ttt[n]
                if S >= T:
                    self.Rank[r[n][0]] = rowSpanIndex[i][0]

        #             [['航海指针', 1, 2], ['又是草帽团情况', 4, 3], ['船员', 5, 2], ['白胡子团', 7, 14], ['其他t', 11, 10]]
        print(data[7:21],titles)
        self.dataClean(data, titles)

        return self.dic

    def processMData(self, MData, headers, Hindex):
        take = []
        for i in MData[Hindex + 1:]:
            if len(i) != len(headers):
                take.append(dict(zip(i[::2], i[1::2])))
            else:
                take.append(dict(zip(headers, i)))
        # print("processMData",take)
        return take

    def processMDtaAgain(self,MData):
        take = []
        for i in MData:
            dic = {}
            if len(i) % 2 != 0:
                dic[i[0]] = dict(zip(i[1:][::2], i[1:][1::2]))
            else:
                dic = dict(zip(i[::2], i[1::2]))
            take.append(dic)
        return take

    def updateDict(self, dics, title, result):

        if dics.get(title):
            value = dics[title]
            # print(result,value,self.dic)
            dics[title] = result
            dics[title].update(value)
        else:
            # print(result,self.dic)

            dics[title] = result

    def he(self, take):
        keys = [k for i in take for k in list(i.keys())]
        if len(set(keys)) == len(keys):
            return {k: v for i in take for k, v in i.items()}
        else:
            return take

    def cleanData(self, title, data):
        MData = []
        for n in data:
            Tindex = n.index(title)
            taks = n[Tindex + 1:]
            if title in self.verticalData or len(taks) % 2 != 0:
                MData.append(taks)
            else:
                t = [taks[i] for i in range(0, len(taks), 2)]
                if len(set(t)) == len(t):
                    MData.append(taks)
                else:
                    MData.extend([taks[i:i + 2] for i in range(0, len(taks), 2)])
        return MData

    def dataClean(self, data, titles):
        IIndex = []

        for t in titles:
            itmes = []
            for itme in range(len(data)):
                # print(data[itme][:-1])
                if t in data[itme][:-1]:
                    itmes.append(data[itme])
            # print(itmes)

        for t in titles:
            itmes = [data[itme] for itme in range(len(data)) if t in data[itme][:len(data[itme])-1] and self.record.get(itme) != data[itme]]
            IIndex.extend([itme for itme in range(len(data)) if t in data[itme][:len(data[itme])-1] and self.record.get(itme) != data[itme]])
            self.record.update({itme: data[itme] for itme in range(len(data)) if t in data[itme][:len(data[itme])-1] and self.record.get(itme) != data[itme]})
            # print("dataClean",t,itmes)
            self.secondClean(t, itmes)
        taks = [data[i] for i in range(len(data)) if i not in IIndex]
        for i in taks:
            take = []
            dic = {i[0]: dict(zip(i[1:][::2], i[1:][1::2]))} if len(i) % 2 != 0 else dict(zip(i[::2], i[1::2]))
            take.append(dic)
            result = self.he(take)
            self.dic |= result
        return True

    def secondClean(self,title,data):
        if not data:
            return None

        MData = self.cleanData(title,data)
        # print("MData", MData)

        n = data[0].index(title)
        dics = self.dic
        for k in data[0][:n]:
            if not dics.get(k):
                dics[k] = {}
            dics = dics[k]
        if title in self.verticalData or self.Rank.get(title):
            Hindex = 0 if not self.Hindex.get(title) else self.Hindex[title]
            headers = MData[Hindex]
            if title in self.verticalData:
                take = self.processMData(MData, headers, Hindex)
            else:
                take = self.processMDtaAgain(MData)

            result = self.he(take)
            self.updateDict(dics, title, result)
        else:
            take = self.processMDtaAgain(MData)
            result = self.he(take)
            self.updateDict(self.dic, title, result)






if __name__ == '__main__':
    verticalData = ['妹子','其他t']
    dirPath = "./演示表格一.html"
    with open(dirPath, mode="r", encoding="utf-8") as f:
        content = f.read()
    et = etree.HTML(content)
    table = et.xpath("//table")[0]
    tier = threeTier(verticalData)
    result = tier.firstAnalysis(table)
    print(result)







