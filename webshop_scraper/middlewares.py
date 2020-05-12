# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.http import TextResponse
from scrapy.utils.response import response_status_message


class AmazonScraperRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        if issubclass(response.__class__, TextResponse):
            page_title = response.css("title::text").get()

            # Retry the request if encountering this page title
            if page_title == "Robot Check":
                return self._retry(request, "Encountered Robot Check.", spider)

        return response
