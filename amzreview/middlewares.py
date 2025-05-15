# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from amzreview.settings import USER_AGENT
from scrapy.http import HtmlResponse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from shutil import which
import logging
import time
from selenium.common.exceptions import TimeoutException

class AmzreviewSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class AmzreviewDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RandomUserAgent(object):

    def process_request(self, request, spider):
        request.headers['User-Agent'] = USER_AGENT



class SeleniumMiddleware:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # 启用无头模式
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--start-maximized")
        # 明确指定 Chrome 二进制文件路径

        chrome_path =  which('chrome')
        chromedriver_path = which('chromedriver')

        logging.info(f"Using Chrome binary: {chrome_path}")
        logging.info(f"Using ChromeDriver binary: {chromedriver_path}")

        chrome_options.binary_location = (chrome_path)
        # === 添加代理设置到 Chrome Options ===
        proxy_server = '172.18.128.1:7899' # 替换成你的代理 IP 和端口
        # 对于 HTTP/HTTPS 代理，使用 --proxy-server 参数
        chrome_options.add_argument(f'--proxy-server={proxy_server}')
        logging.info(f"Setting Chrome proxy to: {proxy_server}")
        # === 代理设置结束 ===

        # 你选择的页面加载策略，'normal' 是默认
        chrome_options.page_load_strategy = 'normal'


        try:
            # === 初始化 driver ===
            self.driver = webdriver.Chrome(service=Service(chromedriver_path),
                                           options=chrome_options)

            # === 在 driver 实例上设置超时时间 ===
            self.driver.set_page_load_timeout(60) # 设置页面加载超时（秒）
            self.driver.set_script_timeout(30) # 设置脚本执行超时（秒），通常 30 秒足够

            logging.info("Selenium WebDriver initialized successfully with proxy settings.")
        except Exception as e:
            logging.error(f"Error initializing Selenium WebDriver: {e}")
            raise

        



        
    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def process_request(self, request, spider):
        if 'selenium' in request.meta:

            # 显示等待页面指定元素出现
            try: 

                print(request.url)
                #1.使用selenium打开请求的url
                self.driver.get(request.url)

                self._accept_cookies()

                self._login()
                # # 将滚动条拖到最底端
                # WebDriverWait(self.driver, 10).until( # 短暂等待 5 秒
                #     EC.element_to_be_clickable((By.XPATH, '//title'))
                # )

                print('xxxxxxxstart')
                WebDriverWait(self.driver, 60).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[starts-with(@id, "customer_review"'))
                )

                time.sleep(20) # 简单等待 2 秒，可以根据需要调整或使用 EC.invisibility_of_element_located

                self.toBottom(self.driver)
                body=self.driver.page_source
                responseUrl = self.driver.current_url

                print('xxxxxxxxend')


                filepath = 'body.html'
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(body)
                    self.logger.info(f"Saved response for {responseUrl} to {filepath}")
                except Exception as e:
                    self.logger.error(f"Failed to save response for {responseUrl} to {filepath}: {e}")


                # 关闭打开的页面
                # self.driver.close()
                return HtmlResponse(
                    url=responseUrl,
                    body=body,
                    encoding='utf-8',
                    request=request
                )
            except TimeoutException:
                # 如果在指定时间内没有找到或点击元素，忽略这个异常，继续执行后续步骤
                logging.info("没有元素.")

                return None
            except Exception as e:
                # 捕获点击或其他操作时可能出现的异常
                logging.warning(f"Error handling blocking element: {e}")

                return None
        
    def _accept_cookies(self):
        
            # --- 2. 检查并操作特定元素 处理 Cookie 同意弹窗
            # 定义你需要检查的元素的 XPath 或 Selector
            # 例如：亚马逊的 Cookie 同意按钮 XPath（这是一个示例，你需要根据实际页面检查）
            cookie_consent_button_xpath = "//input[@data-action='a-popover-accept']" # 示例XPath

            # === 第一次检查：快速查找 ===
            logging.info(f"Quickly checking for blocking element: {cookie_consent_button_xpath}")
            # find_elements 不会等待（除非有隐式等待），立即返回列表
            elements = self.driver.find_elements(By.XPATH, cookie_consent_button_xpath)

            if not elements:
                return
            # 或 CSS Selector: "input[data-action='a-popover-accept']"

            # 使用 WebDriverWait 检查元素是否出现并可点击，设置一个较短的超时时间，
            # 如果元素不存在或不可点击，会在超时后抛出 TimeoutException
            try:
                logging.info(f"Checking for blocking element: {cookie_consent_button_xpath}")
                blocking_element = WebDriverWait(self.driver, 5).until( # 短暂等待 5 秒
                    EC.element_to_be_clickable((By.XPATH, cookie_consent_button_xpath))
                )
                logging.info("Blocking element found. Clicking...")
                blocking_element.click()
                logging.info("Blocking element clicked.")

                # 点击后页面可能会有变化，可能需要短暂等待新内容加载或旧元素消失
                # 可以用 time.sleep(或更智能地等待某个元素出现或消失)
                time.sleep(2) # 简单等待 2 秒，可以根据需要调整或使用 EC.invisibility_of_element_located

            except TimeoutException:
                # 如果在指定时间内没有找到或点击元素，忽略这个异常，继续执行后续步骤
                logging.info("No blocking element found or not clickable within time.")
            except Exception as e:
                    # 捕获点击或其他操作时可能出现的异常
                    logging.warning(f"Error handling blocking element: {e}")

     

    def _login(self): 
        login_email_xpath = '//input[@id="ap_email_login"]'

        logging.info(f"Quickly checking for login element: {login_email_xpath}")
        # find_elements 不会等待（除非有隐式等待），立即返回列表
        elements = self.driver.find_elements(By.XPATH, login_email_xpath)

        if not elements:
            logging.info(f"没有登录的 element")
            return
        logging.info(f"有登录的 element", elements)

        try:
            logging.info(f"Checking for login element: {login_email_xpath}")
            username_box = WebDriverWait(self.driver, 5).until( # 短暂等待 5 秒
                EC.element_to_be_clickable((By.XPATH, login_email_xpath))
            )
            logging.info("enter email...")
            username_box.send_keys('xxxxxxxxxx')
            submit_email_button = WebDriverWait(self.driver, 5).until( # 短暂等待 5 秒
                EC.element_to_be_clickable((By.XPATH, '//input[@class="a-button-input" and @type="submit" and @aria-labelledby="continue-announce"]'))
            )
            submit_email_button.click()
            logging.info("click continue button.")

            # 点击后页面可能会有变化，可能需要短暂等待新内容加载或旧元素消失
            # 可以用 time.sleep(或更智能地等待某个元素出现或消失)
            time.sleep(2) # 简单等待 2 秒，可以根据需要调整或使用 EC.invisibility_of_element_located

            login_password_xpath = '//input[@id="ap_password"]'

            logging.info(f"Checking for login element: {login_password_xpath}")
            password_box = WebDriverWait(self.driver, 5).until( # 短暂等待 5 秒
                EC.element_to_be_clickable((By.XPATH, login_password_xpath))
            )
            logging.info("enter password...")
            password_box.send_keys('xxxxxxxxx')

            submit_login_button = WebDriverWait(self.driver, 5).until( # 短暂等待 5 秒
                EC.element_to_be_clickable((By.XPATH, '//input[@id="signInSubmit" and @type="submit"]'))
            )
            submit_login_button.click()
            logging.info("click submit button.")



        except TimeoutException:
            # 如果在指定时间内没有找到或点击元素，忽略这个异常，继续执行后续步骤
            logging.info("No blocking element found or not clickable within time.")
        except Exception as e:
                # 捕获点击或其他操作时可能出现的异常
                logging.warning(f"Error handling blocking element: {e}")


    def spider_closed(self, spider):
    	#注销chrome实例
        self.driver.quit()
        
    def toBottom(self,driver):
        driver.execute_script("document.documentElement.scrollTop = 100000")


class ProxyMiddleware:
    def process_request(self, request, spider):
        request.meta['proxy'] = 'http://172.18.128.1:7899'