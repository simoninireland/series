# -*- coding: utf-8 -*-

# Copyright (c) 2024, Simon Dobson <simoninireland@gmail.com>

# Permission is hereby granted, free of charge, to any
# person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice
# shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
# OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import blinker
from nikola.plugin_categories import SignalHandler


class Series(SignalHandler):

    name = "series"

    def orderPosts(self, lang, posts):
        '''Put the posts into order.

        Posts are by default put into order of increasing date. If
        any posts have a 'category_order' metadata value, this is used
        instead. Category orders can be real numbers to allow posts
        to slot into place.

        :param lang: the current language
        :param posts: the posts
        :returns: the posts in sorted order
        '''
        series = []
        for p in posts:
            series.append(p)

        # sort by increasing order of date
        series.sort(key=lambda p: p.meta[lang]['date'])

        # run through the posts and add date irdering to any
        # posts without an explicit position
        for i in range(len(series)):
            if 'category_order' not in series[i].meta[lang].keys():
                series[i].meta[lang]['category_order'] = float(i + 1)

        # sort into category ordering
        series.sort(key=lambda p: float(p.meta[lang]['category_order']))

        return series


    def wireSeriesTogether(self, series):
        '''Set the next and previous links on posts to be within
        their series, not within their times.

        :param series: the posts
        :returns: the posts (list unchanged)'''

        # next post in chain
        for i, p in enumerate(series[:-1]):
            p.next_post = series[i + 1]
        series[-1].next_post = None

        # previous post in chain
        for i, p in enumerate(series[1:]):
            p.prev_post = series[i]
        series[0].prev_post = None

        return series


    def buildSeries(self, lang, cat, posts):
        '''Build the series from a category.

        :param lang: the current language
        :param cat: the category
        :param posts: the posts in the category
        '''
        series = self.orderPosts(lang, posts)
        self.wireSeriesTogether(series)


    def buildAllSeries(self, site):
        '''Build all the series, one per category.
        '''
        for lang, langposts in site.posts_per_classification['category'].items():
            for cat, posts in langposts.items():
                self.buildSeries(lang, cat, posts)


    def set_site(self, site):
        '''Set the site.

        :param site: the site (Nikola instance)
        '''
        super().set_site(site)

        # After taxonomies_classifier has set site.posts_per_classification,
        # construct the series
        blinker.signal("taxonomies_classified").connect(self.buildAllSeries)
