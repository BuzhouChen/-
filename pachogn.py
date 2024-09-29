import pandas as pd
import selenium  # 导入Selenium库
from selenium import webdriver  # 从Selenium中导入webdriver
from selenium.webdriver.common.by import By  # 导入By类用于定位元素
from selenium.webdriver.support.wait import WebDriverWait  # 导入WebDriverWait类用于显式等待
from selenium.webdriver.support import expected_conditions as EC  # 导入expected_conditions类用于定义等待条件
from time import sleep  # 导入sleep函数用于等待
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException  # 导入Selenium常见的异常
from selenium.webdriver.common.keys import Keys  # 导入Keys类用于模拟键盘操作
import ddddocr  # 导入ddddocr库用于处理验证码
import base64  # 导入base64库用于处理Base64编码
from selenium.webdriver import ActionChains  # 导入ActionChains类用于模拟复杂的用户操作
import random  # 导入random库用于生成随机数
from PIL import Image  # 导入PIL库中的Image类用于图像处理
import os  # 导入os库用于文件操作
import requests # 下载图片
import re # 正则表达式


def handle_img(img_src: str, name: str, size: tuple, name_sized: str):
    """
    对下载的验证码图片进行处理
    :param img_src: 原图片编码
    :param name: 保存名称
    :param size: 调整的大小，元组(width, height)
    :param name_sized: 调整后的图片名
    :return: 无
    """
    if not os.path.exists('images'):  # 检查images目录是否存在
        os.makedirs('images')  # 创建images目录
    s_img = img_src.replace('data:image/png;base64,', '')  # 去除Base64前缀
    img_byte = base64.b64decode(s_img)  # 解码Base64编码的图片
    with open(f"images/{name}.png", "wb") as f:  # 以二进制写入方式打开文件
        f.write(img_byte)  # 将图片写入文件
    img = Image.open(f"images/{name}.png")  # 打开图片文件
    res_img = img.resize(size)  # 调整图片大小
    res_img.save(f"images/{name_sized}.png")  # 保存调整后的图片



def get_distance(tg_img, bg_img):
    """
    获取滑动距离
    :param bg_img: 底层大图片
    :param tg_img: 滑块小图片
    :return: 返回距离
    """
    with open(f"images/{tg_img}.png", "rb") as f:  # 打开目标图片文件
        tg = f.read()  # 读取文件内容
    with open(f"images/{bg_img}.png", "rb") as f:  # 打开背景图片文件
        bg = f.read()  # 读取文件内容
    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)  # 创建ddddocr对象
    res = det.slide_match(tg, bg, simple_target=True)  # 使用ddddocr进行滑块匹配
    return res['target'][0]  # 返回滑动距离

def move_mouse(browser, distance, element):
    """
    轨迹模拟方法（三段随机速度）成功几率高
    :param browser: 浏览器driver对象
    :param distance: 移动距离
    :param element: 移动的元素
    :return: 无返回值
    """
    has_gone_dist = 0  # 已移动距离
    remaining_dist = distance  # 剩余距离
    ActionChains(browser).click_and_hold(element).perform()  # 点击并按住元素
    sleep(0.5)  # 等待0.5秒
    while remaining_dist > 0:  # 当剩余距离大于0时
        ratio = remaining_dist / distance  # 计算已移动的比例
        if ratio < 0.1:  # 如果已移动比例小于0.1
            span = random.randint(3, 5)  # 随机生成移动距离
        elif ratio > 0.9:  # 如果已移动比例大于0.9
            span = random.randint(5, 8)  # 随机生成移动距离
        else:  # 如果已移动比例在0.1到0.9之间
            span = random.randint(15, 20)  # 随机生成移动距离
        ActionChains(browser).move_by_offset(span, random.randint(-5, 5)).perform()  # 移动鼠标
        remaining_dist -= span  # 更新剩余距离
        has_gone_dist += span  # 更新已移动距离
        sleep(random.randint(5, 20) / 100)  # 随机等待
    ActionChains(browser).move_by_offset(remaining_dist, random.randint(-5, 5)).perform()  # 移动剩余距离
    ActionChains(browser).release(on_element=element).perform()  # 释放鼠标

def handle_captcha(browser):
    """
    处理验证码的函数
    :param browser: 浏览器对象
    :return: 验证码处理成功返回True，否则返回False
    """
    try:
        captcha = browser.find_element(By.XPATH, '//div[@class="JDJRV-bigimg"]/img')  # 获取验证码图片背景大图
        captcha_img = captcha.get_attribute('src')  # 获取验证码图片的src属性
        captcha_size = (captcha.size['width'], captcha.size['height'])  # 获取验证码图片的大小
        handle_img(captcha_img, 'bg', captcha_size, 'bg_sized')  # 处理验证码背景图片
        wrap = browser.find_element(By.XPATH, '//div[@class="JDJRV-smallimg"]/img')  # 获取滑块小图
        wrap_img = wrap.get_attribute('src')  # 获取滑块图片的src属性
        wrap_size = (wrap.size['width'], wrap.size['height'])  # 获取滑块图片的大小
        handle_img(wrap_img, 'sm', wrap_size, 'sm_sized')  # 处理滑块图片
        distance = get_distance("sm_sized", "bg_sized")  # 计算滑动距离
        print(distance)  # 打印滑动距离
        move_mouse(browser, distance, wrap)  # 进行滑动
        return True  # 返回True表示验证码处理成功
    except NoSuchElementException as msg:  # 如果出现NoSuchElementException异常
        print("无法获取验证码元素:", msg)  # 打印异常信息
        return False  # 返回False表示验证码处理失败



def get_text_selenium(driver, xpath):
    """
    获取元素文本内容
    :param driver: 浏览器driver对象
    :param xpath: 元素的XPath路径
    :return: 返回元素的文本内容，如果找不到元素返回空字符串
    """
    try:
        return driver.find_element(By.XPATH, xpath).text.strip()  # 获取元素的文本内容并去除首尾空格
    except (NoSuchElementException, StaleElementReferenceException):  # 如果出现NoSuchElementException或StaleElementReferenceException异常
        return ""  # 返回空字符串



def get_attribute_selenium(driver, xpath, attribute):
    """
    获取元素的指定属性值
    :param driver: 浏览器driver对象
    :param xpath: 元素的XPath路径
    :param attribute: 要获取的属性名称
    :return: 返回元素的属性值，如果找不到元素或属性返回空字符串
    """
    try:
        return driver.find_element(By.XPATH, xpath).get_attribute(attribute)  # 获取元素的指定属性值
    except (NoSuchElementException, StaleElementReferenceException):  # 如果出现NoSuchElementException或StaleElementReferenceException异常
        return ""  # 返回空字符串


def getDetails(driver, id):
    driver.implicitly_wait(4)
     # 尝试获取 Catag
    try:
        Catag = driver.find_element(By.XPATH, '//*[@id="crumb-wrap"]/div/div[1]/div[5]/a').text.strip()
    except:
        Catag = ''  # 如果找不到元素，则返回空值

    # 尝试获取 Brand
    try:
        Brand = driver.find_element(By.XPATH, '//*[@id="parameter-brand"]/li/a').text.strip()
    except:
        Brand = ''  # 如果找不到元素，则返回空值

            

   # 尝试获取 Size
    try:
        Size = driver.find_element(By.XPATH, '//div/div/div/div/div[@class="item  selected"]/a').text.strip()
    except:
        Size = ''  # 如果找不到元素，则返回空值

    # 尝试获取图片链接并下载图片
    try:
        link = driver.find_element(By.XPATH, '//img[@id="spec-img"]').get_attribute('src')
        response = requests.get(link)
        # 保存图片
        if not os.path.exists('savePic'):  # 检查savePic目录是否存在
            os.makedirs('savePic')  # 创建savePic目录
        with open(f'./savePic/{id}.jpg', 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded and saved as {id}.jpg")

    except:
        link = ''  # 如果找不到图片链接，则返回空值

    return Catag, Brand, Size



user_input = input("请输入要搜索内容：")  # 获取用户输入的搜索内容
page_count = int(input("请输入要爬取的页数："))  # 获取用户输入的要爬取的页数
# 第1页爬的最全
# 爬不到的是空值


# user_input = ""  # 获取用户输入的搜索内容
# page_count =   # 获取用户输入的要爬取的页数


wb = webdriver.Chrome()  # 创建Chrome浏览器对象
wb.set_page_load_timeout(5)  # 设置页面加载超时时间为5秒
try:
    wb.get('https://www.jd.com/')  # 打开京东首页
except selenium.common.exceptions.TimeoutException:
    pass  # 如果加载超时，继续执行
wb.implicitly_wait(5)  # 设置隐式等待时间为5秒

login_button = WebDriverWait(wb, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#ttbar-login > a.link-login > span.style-red'))
)  # 等待并找到登录按钮
login_button.click()  # 点击登录按钮

username_field = WebDriverWait(wb, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#loginname'))
)  # 等待并找到用户名输入框
username_field.send_keys('username')  # 输入你的用户名

password_field = WebDriverWait(wb, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '#nloginpwd'))
)  # 等待并找到密码输入框
password_field.send_keys('password')  # 输入你的密码

submit_button = WebDriverWait(wb, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, '#loginsubmit'))
)  # 等待并找到登录提交按钮
submit_button.click()  # 点击提交按钮
sleep(2)  # 等待2秒

while True:  # 循环处理验证码
    try:
        captcha_element = WebDriverWait(wb, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="JDJRV-bigimg"]/img'))
        )  # 等待验证码元素出现
        handle_captcha(wb)  # 调用handle_captcha函数处理验证码
        sleep(2)  # 等待2秒
    except TimeoutException:  # 如果等待超时，表示验证码已经处理完毕
        break  # 退出循环


productInfo = []


try:
    driver = webdriver.Chrome()
    
    search = WebDriverWait(wb, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#key'))
    )  # 等待并找到搜索框
    search.clear()  # 清空搜索框
    search.send_keys(user_input)  # 输入搜索关键字
    search_btn = WebDriverWait(wb, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#search > div > div.form > button > i'))
    )  # 等待并找到搜索按钮
    search_btn.click()  # 点击搜索按钮
    sleep(10)  # 等待搜索结果加载
    

    for page in range(1, page_count + 1):  # 循环遍历指定页数
        print(f"正在爬取第 {page} 页")  # 打印当前爬取的页数
        # sleep(random.randint(5, 20) / 100)
        items = wb.find_elements(By.XPATH, '//li[@class="gl-item"]')  # 查找当前页的所有商品项
        for item in items:  # 遍历所有商品项
            name = get_text_selenium(item, './/div[contains(@class, "p-name")]//em')  # 获取商品名称
            price = get_text_selenium(item, './/div[contains(@class, "p-price")]//i')  # 获取商品价格
            link = get_attribute_selenium(item, './/div[contains(@class, "p-img")]//a', 'href')  # 获取商品链接
            if link and not link.startswith('http'):  # 如果链接不完整，补全链接
                link = 'https:' + link
            product = []
            # print(f"商品名称: {name}")  # 打印商品名称
            # print(f"商品价格: {price}")  # 打印商品价格
            # print(f"商品链接: {link}")  # 打印商品链接
            # 正则表达式
            getID = r"item.jd.com/(\d+).html"
            id = re.search(getID , link).group(1)
            print(id)
            
            driver.get(link)
            catag, brand, size = getDetails(driver, id)
            
            remark = int(100)
            
            product.append(id)    # 商品编号
            product.append(brand)    # 品牌
            product.append(name)    # 商品名称
            product.append(size)    # 规格
            product.append(price)   # 价格
            product.append(remark)  # 好评度
            product.append(catag)   # 类别
            product.append(link)    # 链接
            
            # product.append(link)    
            productInfo.append(product)
            
            print("-" * 50)  # 分隔符
        if page < page_count:  # 如果还没有爬取完指定页数
            try:
                next_button = WebDriverWait(wb, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '.pn-next'))
                )  # 等待并找到下一页按钮
                next_button.click()  # 点击下一页按钮
                sleep(5)  # 等待新一页加载
            except:  # 如果无法加载下一页
                print(f"无法加载下一页，已爬取 {page} 页")  # 打印错误信息
                break  # 退出循环
finally:
    driver.quit()
    wb.quit()  # 关闭浏览器
    



name = ['商品编号','品牌','商品名称','规格','价格','好评度','类别','链接']
save2file =pd.DataFrame(columns=name,index=None,data=productInfo)
if not os.path.exists('csv'):  # 检查csv目录是否存在
    os.makedirs('csv')  # 创建csv目录
save2file.to_csv('./csv/productInfo.csv',index=None)




