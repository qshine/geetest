#!/usr/bin/env python
# coding:utf-8

import re
import random
import json
import time
import requests
from PIL import Image
from js.userresponse import userresponse


"""
1.  http://uems.sysu.edu.cn/jwxt/StartCaptchaServlet?ts=0.1331373238700324    ts是一个随机数, 无所谓
2.  http://api.geetest.com/getfrontlib.php?gt=80a8ed78d1d22e16f5b6c478f03b9212&callback=geetest_1491023377357
3.  http://api.geetest.com/get.php?gt=80a8ed78d1d22e16f5b6c478f03b9212&challenge=de92230d518d69c432c440d48b3f3a00&product=float&offline=false&type=slide&callback=geetest_1491023375682

"""

class GeetestHandler(object):
    def __init__(self):
        self.s = requests.Session()

    def start(self):
        """先请求首页地址得到cookie"""
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Host': 'uems.sysu.edu.cn',
            'Upgrade-Insecure-Requests': 1,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        r = self.s.get('http://uems.sysu.edu.cn/jwxt/', headers=headers)
        return dict(r.cookies)



    def setup_1(self, cookies):
        setup1_url = 'http://uems.sysu.edu.cn/jwxt/StartCaptchaServlet?ts={}'
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            # 'Cookie': ''.join([cookies.keys()[0], '=', cookies.values()[0]]),
            'Connection': 'keep-alive',
            'Referer': 'http://uems.sysu.edu.cn/jwxt/',
            'Host': 'uems.sysu.edu.cn',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        url = setup1_url.format(random.random())
        r = self.s.get(url, headers=headers, cookies=cookies)
        cont = json.loads(r.text)
        res = (cont.get('gt'), cont.get('challenge'))
        return res

    def setup_2(self, gt, cookies):
        """
        parseInt(Math.random() * 10000) + (new Date()).valueOf()变为python代码
        :return:
        """
        setup2_url = 'http://api.geetest.com/getfrontlib.php?gt={}&callback=geetest_{}'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Referer': 'http://uems.sysu.edu.cn/jwxt/',
            'Host': 'api.geetest.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        param = int(random.random()*100000 + time.time()*1000)
        r = self.s.get(setup2_url.format(gt, param), headers=headers, cookies=cookies)
        # 先不管内容是什么
        return param

    def setup_3(self, gt, challenge, cookies):
        setup3_url = 'http://api.geetest.com/get.php?gt={}&challenge={}&product=float&offline=false&type=slide&callback=geetest_{}'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            # 'Cookie': ''.join([cookies.keys()[0], '=', cookies.values()[0]]),
            'Connection': 'keep-alive',
            'Referer': 'http://uems.sysu.edu.cn/jwxt/',
            'Host': 'api.geetest.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }

        digit = int(random.random()*100000 + time.time()*1000)
        patt = re.compile(r'geetest_%d\((.*?)\)'%digit)
        url = setup3_url.format(gt, challenge, digit)

        # 得到返回结果
        r = self.s.get(url, headers=headers, cookies=cookies)
        res = json.loads(re.search(patt, r.text).group(1))

        # 下载三张图片
        for key in ['slice', 'bg', 'fullbg']:
            r = requests.get('http://static.geetest.com/'+res[key])
            with open('%s.jpg'%key, 'wb') as f:
                f.write(r.content)
        # 最后一步要用一个34位的challenge
        challenge_34 = res['challenge']
        return challenge_34

    def reset_img(self):
        """
        图片还原
        var a = function() {
            for (var a, b = "6_11_7_10_4_12_3_1_0_5_2_9_8".split("_"), c = [], d = 0, e = 52; d < e; d++)
                a = 2 * parseInt(b[parseInt(d % 26 / 2)]) + d % 2,
                parseInt(d / 2) % 2 || (a += d % 2 ? -1 : 1),
                a += d < 26 ? 26 : 0,
                c.push(a);
            return c
        }
        ......
        var m, n = a(), o = document.createElement("div");
        for (o.className = "gt_cut_" + b + "_slice",
                i = 0,
                j = n.length; i < j; i++)
                    k = "-" + (n[i] % 26 * 12 + 1) + "px " + (n[i] > 25 ? -f.config.height / 2 : 0) + "px",
                    m = o.cloneNode(),
                    m.style.backgroundImage = "url(" + c + ")",
                    l.push(m),
                    e.appendChild(m),
                    m.style.backgroundPosition = k
        """
        # 位置参数
        a = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12,
             13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]

        for name in ['bg', 'fullbg']:

            # 打开图片
            im = Image.open(name+'.jpg')

            # Creates a new image with the given mode and size
            # PIL.Image.new(mode, size, color=0)
            # 还原后的图片 长, 宽=260, 116
            im_new = Image.new("RGB", (260, 116))
            # 得到图像大小
            width, height = im.size

            # TODO there is question about reset img
            for row in range(2):
                for column in range(26):
                    right = a[row * 26 + column] % 26 * 12 + 1
                    down = 58 if a[row * 26 + column] > 25 else 0
                    # 单个小方块的 宽w和高h
                    for w in range(10):
                        for h in range(58):
                            ht = 58 * row + h
                            wd = 10 * column + w
                            # 从原图得到给定位置的像素放到新的图片
                            value = im.getpixel((w + right, h + down))
                            # put the value into given position
                            im_new.putpixel((wd, ht), value)

            im_new.save(name+'_after.jpg')


    def userresponse(l, challenge):
        """翻译的js代码, 构造userresponse"""
        a = challenge[-2:]
        func = lambda x: x - 87 if x > 57 else x - 48
        d = [func(ord(a[i])) for i in range(len(a))]
        c = 36 * d[0] + d[1]
        g = int(l) + c
        b = challenge[0:32]
        i = [[], [], [], [], []]
        j = {}
        k = 0

        for h in b:
            if h not in j:
                j[h] = 1
                i[k].append(h)
                k += 1
                k = 0 if 5 == k else k
        n = g
        o = 4
        p = ""
        q = [1, 2, 5 ,10, 50]
        while n > 0:
            if n - q[o] >= 0:
                m = int(random.random()*len(i[o]))
                p += i[o][m]
                n -= q[o]
            else:
                i.pop(o)
                q.pop(o)
                o -= 1
        return p


    def params_a(self, distance):
        """
        以下为第四步请求时的参数a构建方法
        """
        def c(a):
            e = []
            f = 0
            g = []
            i = len(a) - 1
            for h in range(i):
                b = int(round(a[h + 1][0] - a[h][0]))
                c = int(round(a[h + 1][1] - a[h][1]))
                d = int(round(a[h + 1][2] - a[h][2]))
                g.append([b, c, d])
                if 0 == b and 0 == c and 0 == d:
                    pass
                elif 0 == b and 0 == c:
                    f += d
                else:
                    e.append([b, c, d + f])
                    f = 0
            if f != 0:
                e.append([b, c, f])
            return e

        def d(a):
            b = "()*,-./0123456789:?@ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqr"
            c = len(b)
            d = ""
            e = abs(a)
            f = e / c
            if f >= c: f = c - 1
            if f: d = b[f]
            e %= c
            g = ""
            if a < 0: g += "!"
            if d: g += "$"
            return g + d + b[e]

        def e(a):
            b = [[1, 0], [2, 0], [1, -1], [1, 1], [0, 1], [0, -1], [3, 0], [2, -1], [2, 1]]
            c = "stuvwxyz~"
            d = 0
            e = len(b)
            while d < e:
                if a[0] == b[d][0] and a[1] == b[d][1]:
                    return c[d]
                else:
                    d += 1
            return 0

        def f(a):
            g = []
            h = []
            i = []
            for j in range(len(a)):
                b = e(a[j])
                if b:
                    h.append(b)
                else:
                    g.append(d(a[j][0]))
                    h.append(d(a[j][1]))
                i.append(d(a[j][2]))
            return "".join(g) + "!!" + "".join(h) + "!!" + "".join(i)

        def roads_arr(dis):
            """
            主要是包含路径的一个数组
            param1： x的偏移距离
            param2： y的偏移距离
            param3： 经历时间
            """

            arr = []
            # 第一个值为点击的位置的相反数, 方块大小是44*44
            first_list = [-random.randint(1, 43), -random.randint(1, 43), 0]
            # 第二个值永远为[0, 0, 0]
            second_param = [0, 0, 0]
            arr.append(first_list)
            arr.append(second_param)

            all_time = 0

            pre_dis = dis - 15  # 最后要放慢速度
            first_slice = pre_dis / 3
            second_slice = (pre_dis * 2) / 3
            total = 0
            while total <= pre_dis:
                if total < first_slice:
                    one_step = random.randint(1, 4)
                    all_time += one_step * random.randint(15, 25)
                elif first_slice <= total < second_slice:
                    one_step = random.randint(2, 3)
                    all_time += one_step * random.randint(15, 25)
                else:
                    one_step = random.randint(1, 2)
                    all_time += one_step * random.randint(15, 25)
                total += one_step
                arr.append([total, random.randint(-2, 2), all_time])
            # 最后加上15个像素的偏移量
            for i in range(10):
                total += 1
                all_time += random.randint(15, 25)
                arr.append([total, random.randint(-2, 2), all_time])
            # 最后5个像素
            while total <= dis:
                one_step = random.randint(0, 1)
                total += one_step
                all_time += random.randint(15, 25)
                arr.append([total, random.randint(-2, 2), all_time])

            return arr

        arr = roads_arr(distance)

        print arr

        tmp = c(arr)
        data = f(tmp)
        passtime = arr[-1][-1]

        return (data, passtime)


    def diff(self, w, h):
        bg_num = self.bg_im.getpixel((w, h))
        fullbg_num = self.fullbg_im.getpixel((w, h))
        # 得到一个元祖
        # TODO 根据一个点来做对么
        tmp = 0
        for i in range(3):
            if abs(bg_num[i]-fullbg_num[i]) > 50:
                tmp += 1
        if tmp == 3:
            return True
        return False


    def get_offset(self):
        """得到偏移量, 按照列进行比较, 单位为像素点"""
        self.bg_im = Image.open('bg_after.jpg')
        self.fullbg_im = Image.open('fullbg_after.jpg')
        width = self.fullbg_im.size[0]
        height = self.fullbg_im.size[1]
        for w in range(width):
            for h in range(height):
                # 如果为真则返回宽度
                if self.diff(w, h):
                    return w
        return False

    def setup_4(self, cookies, gt, challenge, offset, callback_param):
        setup4_url = 'http://api.geetest.com/ajax.php'
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Referer': 'http://uems.sysu.edu.cn/jwxt/',
            'Host': 'api.geetest.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        }
        user_response = userresponse(offset, challenge)
        img_load = str(random.randint(0, 200) + 50)
        a, passtime = self.params_a(offset)
        # 请求的参数
        params = {
            'gt': gt,
            'challenge': challenge,
            'userresponse': user_response,
            'passtime': passtime,
            'imgload': img_load,
            'a': a,
            'callback': 'geetest_'+str(callback_param)
        }

        time.sleep(passtime/1000+3)
        print '马上开始请求......'
        r = self.s.get(setup4_url, headers=headers, cookies=cookies, params=params)
        print r.url
        print r.content



    def run(self):
        cookies = self.start()
        gt, challenge = self.setup_1(cookies)
        callback_param = self.setup_2(gt, cookies)
        challenge_34 = self.setup_3(gt, challenge, cookies)
        self.reset_img()
        offset = self.get_offset()
        if offset:
            self.setup_4(cookies, gt, challenge_34, offset, callback_param)
        self.s.close()




if __name__ == '__main__':
    for i in range(10):
        g = GeetestHandler()
        g.run()
        print '^^^^^^^^^^^^^^^^'
    # l = 39
    # b = "48a2f8d48867b29fe889760f120289e7ez"
    # print ba_t(l, b)

    # arr = [
    #     # 开始
    #     [1, 352],
    #     [4, 365],
    #     [7, 372],
    #     [10, 386],
    #     [14, 398],
    #     [18, 410],
    #     [22, 422],
    #     [25, 434],
    #     [28, 446],
    #
    #     # 中间
    #     [34, 506],
    #     [34, 528],
    #     [35, 542],
    #     [35, 554],
    #     [40, 589],
    #
    #     # 中后
    #     [70, 1043],
    #     [70, 1054],
    #     [71, 1078],
    #     [72, 1186],
    #     [75, 1281],
    #     [75, 1350],
    #
    #     # 最后
    #     [77, 1388],
    #     [77, 1400],
    #     [77, 1412],
    #     [77, 1424],
    #     [77, 1544],
    #     [78, 1564],
    #     [78, 1974],
    # ]
    #
    # # 78是真实的偏移距离
    # # 1974是 passtime
    #
    #
    #
    #

















