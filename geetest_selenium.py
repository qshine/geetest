#!/usr/bin/env python
# coding:utf-8

import re
import time
import random
import logging
import requests
from PIL import Image
from bs4 import BeautifulSoup
from config import driver, HOST_URL
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.command import Command
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import logging
logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

logging.basicConfig(level=logging.DEBUG)



class SeleniumHandler(object):
    """
    主要操作鼠标完成查询和拼接验证码的动作
    """
    def __init__(self):
        self.driver = driver
        self.driver.maximize_window()
        self.page_source = None
        self.verify_nums = 0    # 验证次数

    def get_imgs(self):
        """下载浏览器请求的两张图片"""
        # background-image: url("http://static.geetest.com/pictures/gt/579066de6/579066de6.webp"); background-position: -265px -58px;

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': 'static.geetest.com',
            'Origin': HOST_URL,
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }

        patt = re.compile(r"""url\("(.*?)"\);""")
        soup = BeautifulSoup(self.page_source, 'lxml')
        all_fullbg_img_urls = soup.find_all('div', attrs={'class': 'gt_cut_fullbg_slice'})
        all_bg_img_urls = soup.find_all('div', attrs={'class': 'gt_cut_bg_slice'})

        fullbg_img_url = re.search(patt, all_fullbg_img_urls[0].attrs['style']).group(1).replace('webp', 'jpg')
        bg_img_url = re.search(patt, all_bg_img_urls[0].attrs['style']).group(1).replace('webp', 'jpg')

        # 下载两张图片
        tf = file("fullbg.jpg", "wb")
        tf.write(requests.get(fullbg_img_url, headers=headers).content)
        tf.close()
        tf = file("bg.jpg", "wb")
        tf.write(requests.get(bg_img_url, headers=headers).content)
        tf.close()


    def reset_img(self):
        """对图片进行复原"""

        # 位置参数
        a = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12,
             13, 23, 22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]

        for name in ['bg', 'fullbg']:
            im = Image.open(name + '.jpg')

            # Creates a new image with the given mode and size
            # PIL.Image.new(mode, size, color=0)
            # 还原后的图片 长, 宽=260, 116
            im_new = Image.new("RGB", (260, 116))
            width, height = im.size

            # 2    2行
            # 26   26列
            # 10   小方块的宽度
            # 58   小方块高度
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
                            # put the value at given position
                            im_new.putpixel((wd, ht), value)
            # 保存为新图片
            im_new.save(name + '_after.jpg')


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

    def move(self, length):
        """对滑块进行拖动, 注意不能一下拖动到目标位置"""
        block = self.driver.find_element_by_css_selector(".gt_slider_knob")
        acthion = ActionChains(self.driver)

        # 保持点击
        acthion.click_and_hold(block).perform()

        roads = self.roads(length)
        # 统计已经走的步数
        total = 0
        for setup in roads:
            total += setup
            self.driver.execute(
                Command.MOVE_TO,
                {
                    'xoffset': setup,
                    'yoffset': random.randint(-1, 1)
                }
            )
            time.sleep(random.randint(39, 698) * 0.0001)
            if total >= length - 15:
                for index in range(3):
                    self.driver.execute(Command.MOVE_TO, {'xoffset': 9999, 'yoffset': 9999})
                    self.driver.execute(Command.MOVE_TO, {'xoffset': -9999, 'yoffset': -9999})
                # 滑块超过一次后把它变为0
                total = 0

        time.sleep(random.randint(0, 100) * 0.001)
        acthion.release(block).perform()

    def roads(self, length):
        """
        规划路径, 如果length太长要加大步长
        """
        # 6为slice的边缘宽度
        len = length - 6
        res = []

        if len < 60:
            for i in range(len):
                res.append(1)
        elif len >= 60 and len < 120:
            total = 0
            for i in range(len/2+1):
                total += 2
                if total <= len:
                    res.append(2)
                else:
                    res.append(len-sum(res))
        else:
            total = 0
            for i in range(len/3+1):
                total += 3
                if total <= len:
                    res.append(3)
                else:
                    res.append(len-sum(res))
        return res


    def query(self, word):
        self.driver.get(HOST_URL)
        # TODO 隐式等待
        time.sleep(3)
        self.page_source = self.driver.page_source
        ele = self.driver.find_element_by_id('keyword')
        ele.clear()
        ele.send_keys(word)
        time.sleep(0.1)
        # click query
        button = self.driver.find_element_by_id('btn_query')
        button.click()
        time.sleep(2)
        self.page_source = self.driver.page_source


    def refresh_captcha(self):
        ele = self.driver.find_element_by_class_name('gt_refresh_button')
        ele.click()

    def get_html(self):
        self.get_imgs()
        logging.info('图片下载成功')
        self.reset_img()
        logging.info('图片恢复成功')
        offset = self.get_offset()
        logging.info('偏移量为: %d'%offset)
        self.move(offset)
        time.sleep(4)
        now_url = self.driver.current_url
        if now_url == HOST_URL:
            html = None
        else:
            html = self.driver.page_source
        return html


    def run(self, keyword):
        self.query(keyword)
        nums = 3
        while nums > 0:
            res = self.get_html()
            if res:
                logging.info('验证成功')
                return res
            else:
                logging.warning('验证没有成功!!!, 再次进行验证......')
                # 删除失败的图片
                # 如果不成功刷新验证码
                self.refresh_captcha()
                time.sleep(3)
                # 重新给self.page_source赋值
                self.page_source = self.driver.page_source
                nums -= 1
        return None



if __name__ == '__main__':
    s = SeleniumHandler()
    print s.run(u'招商银行')


