
# JD-Web-Crawler
 京东数据爬取（不完全匹配版）     
***声明：本程序仅作为学习交流使用！侵删***

## 前置条件   
确保你已经安装了以下Python库：   
Selenium：用于自动化浏览器操作    
ddddocr：用于处理验证码   
Pillow (PIL)：用于图像处理   
chromedriver：用于驱动Chrome浏览器   
re: 正则表达式   


## 代码结构   
建议主要参考参考资料网址。   

新增函数`getDetails(driver, id)`用来获取品类、品牌和尺码，无法匹配则返回空值。
我用来爬服装领域的，其他领域可能不匹配。可以自己写正则表达式来匹配。


## 使用指南

将`username_field.send_keys('username')`的username换成自己京东的用户名，将`password_field.send_keys('password')`换成自己的密码。



## 参考资料
[使用Selenium与ddddocr实现京东通过自动验证码商品爬虫的完整指南](https://blog.csdn.net/AKALuo10/article/details/141420887)
