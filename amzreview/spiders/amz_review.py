import scrapy
import os


class AmzReview(scrapy.Spider):
    name = 'amzreview'
    start_urls = ['https://www.amazon.com/product-reviews/xxxxxxxxxxxx/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews']
    allowed_domains = ['www.amazon.com']
    # headers = {
    #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #     'Accept-Language': 'en-US,en;q=0.5',
    #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    #     'Cookie': 'session-id=257-7010412-1957450; x-amz-captcha-1=1744364813193258; x-amz-captcha-2=dOHzU1r7+2GB1dW/IiZ2eQ==; ubid-acbde=259-9869248-6960243; lc-acbde=en_GB; i18n-prefs=GBP; at-acbde=Atza|IwEBIBD8FcNUtuTCVtEMRIGefriSpS04VCP3Sbv2M-fSZdhDTlBeP_o7fd-YIBKxVVdGKAoWg2qSYkYgv351uu-BwQe2lNvT32b9eVYCcnPZmY2YC2NZg4_wwSSVcj3q8cisx4XyfMl7nFqTVT7Mdeak1OefJSyaf-RamXFc4cmLYwNvfOomY53YCYVdaVJ8gbme4q3VObGUnfdLIup2GV48f8z6IdLvLFIy6P4VOiS5a5ZAUtrdexd1IkdLjlSJ5W1NJ98; sess-at-acbde="ZwFylIac1D16gxAdrga+Kb/iivBQKwq2LozjAdLYkxc="; sst-acbde=Sst1|PQExNcTWq3RjZp2_s6BBlO0FCRSq1LZFR10XOrcmpSFgzJ1XRtkrDOh98NhuglJfis0DHi6YeVuZgaDfbxStXE-q0JYm6HdX-pSgtPTTMmHg9HbNdDENUtFPmKGI2ZoWQ9Gfd2ZYrhojkThP3agFEtaXlGDQB3ABN0vjBMF1nEHiPhvRbQdhP_r5NKVYnYicj3yUq0-yHaQ3vAA2ES_-0nk5dvdj8jY8XCHk1Bofn4x3oIP8qusrFT4q3WxlyC3FijZ-WGE757mh7ZyspolP__BHRJYZh94SxAuRUCHsKwDINnI; session-id-time=2082787201l; sp-cdn="L5Z9:JP"; session-token=DNgNbpYMYaK3rZKobKB1PqZ0WZNuJsvtHfIeimb1seIEyjf58rDC6mzyycAxHP4Ly+iAkhOShhE6b7qAgvALY50WBhrsPbD4JXYXFkCiY79qWDyWMI7+q0fslJPd9rfylqE9E1EMCcG6rkBhOKQ04Ui0Q3xJPYNced2Rqs8c1XKxUv+pCXJ20Ec0y+aYCItnyy66hG7lYnUA7L9/ENLOHDIvQCVX5h75PJLzTWP7yP+9TUS1nCu+lHm9deDN8ZNXJP3tlkNdrRBs1x71Yx5f8Q5jbTiQMgjS5/bZfTFdIJHrwD1LwHSeb4vPy5ouQd48++d+WsmHp76PeaALkFPexxXG6IIgr3/3YcnZfo17MaaEvb/Sl7zYdwd3jcfIk2b9; x-acbde="v3FZ7bwVFhbPabDVpQagd@f16RiDIY?uK7BkSZWufwAknAW0PmaP80zOiTni1mjG"; csm-hit=tb:XQ4077VWHYPDP014VAQJ+s-RH9PZP245WKR3KW7R797|1747130049501&t:1747130049501&adb:adblk_no; rxc=ABn537h7RS9bSn562eM"'
    # }

    headers = {
        'Host': 'www.amazon.com',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; \
                        SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Version/4.0 \
                        Chrome/65.0.3325.109 Mobile Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def parse(self, response):


        try:

            print('a', response)
            print("页面标题：", response.xpath('//title/text()').get())

            # print(response.text)  # 打印完整的HTML内容

            # 3. 将 response.text 写入文件

            filepath = 'data.html'
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.logger.info(f"Saved response for {response.url} to {filepath}")
            except Exception as e:
                self.logger.error(f"Failed to save response for {response.url} to {filepath}: {e}")


            if "Sign-In" in response.text or "authportal" in response.url:
                print("被重定向到登录页了")


            reviews = response.css('[id^="customer_review-"]')

            for review in reviews:
                print(review.get())

            # 尝试提取评论内容（示例 XPath）
            reviews = response.xpath('//div[contains(@id, "customer_review")]')
            for review in reviews:
                title = review.xpath('.//a[@data-hook="review-title"]/span/text()').get()
                rating = review.xpath('.//i[@data-hook="review-star-rating"]//text()').get()
                body = review.xpath('.//span[@data-hook="review-body"]/span/text()').get()
                print("标题:", title)
                print("评分:", rating)
                print("内容:", body)

        except Exception as e:
                # 捕获点击或其他操作时可能出现的异常
                self.logger.warning(f"Error handling blocking element: {e}")


    def start_requests(self):
        # print(self.headers)
        for url in self.start_urls:
            yield scrapy.Request(url=url, meta={'selenium': True})

            # yield SeleniumRequest(url=url, callback=self.parse)
            # yield SeleniumRequest.Request(url=url, callback=self.parse)