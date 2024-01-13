# series.py -- Turn blog categories into series or blogchains

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


class SeriesRep:
    '''A representation for a series that includes all the methods
    needed to construct links and tables of contents. The actual
    layout of these items is left to templates.

    :param posts: the posts in the series, in the desired order

    '''

    def __init__(self, posts, title = None):
        self._posts = posts
        self._title = title


    def inSeriesLinks(self):
        '''Set the next and previous links on posts to be within the
        series, not within the timeline.

        '''

        # next post in chain
        for i, p in enumerate(self._posts[:-1]):
            p.next_post = self._posts[i + 1]
        self._posts[-1].next_post = None

        # previous post in chain
        for i, p in enumerate(self._posts[1:]):
            p.prev_post = self._posts[i]
        self._posts[0].prev_post = None


    def __getitem__(self, i):
        '''Return the i'th post in the series, zero-based.

        :param i: the index
        :returns: the post'''
        return self._posts[i]


    def numberOfPosts(self):
        '''Return the number of posts in the series.

        :returns: the number of posts

        '''
        return len(self._posts)


    def title(self):
        '''Return the title of the series.

        This is by default the title of the first post, but this can
        be overridden.

        :returns: the title of the series.

        '''
        if self._title:
            return self._title
        else:
            return self._posts[0].title()


    def indexOf(self, post):
        '''Return the index of the post in the series.

        Indices are zero-based and used to index into the series.

        :param post: the post
        :returns: the post's index

        '''
        return self._posts.index(post)


    def numberOf(self, post):
        '''Return the number of the post in the series.

        Indices are one-based, which is easier to read when presented
        on the page.

        :param post: the post
        :returns: the post's number

        '''
        return self.indexOf(post) + 1

    def indicesAround(self, post, n):
        '''Return the indices of the n posts around the given post in
        the series.

        :param post: the focal post
        :param n: the number of posts requested
        :returns: the indices at either end of the posts'''
        i = self.indexOf(post)
        m = self.numberOfPosts()

        # make sure we have an even number either side, which
        # implies we can always move in either direction
        if (n % 2) == 0:
            n += 1

        # basic position centred on post
        first = i - int((n - 1) / 2)
        last = first + n - 1

        # slide the window if necessary
        if first < 0:
            last = min(last + abs(first), m - 1)
            first = 0
        if last >= m:
            first = max(m - n, 0)
            last = m - 1

        return first, last


    def postsAround(self, post, n):
        '''Return a list of n posts centred on the given post.

        This may not return n posts, if the series is less than n
        items long; the posts will not be centred on i if there are
        fewer than n/2 items before.

        :param post: the focal post
        :param n: the number of posts requested
        :returns: a list of posts

        '''
        first, last = self.indicesAround(post, n)
        return self._posts[first:last + 1]


    def includesFirstPost(self, post, n):
        '''Test if the posts around the given post include the first
        post in the series.

        :param post: the post
        :param n: the number of posts displayed around
        :returns: True if these posts include the first one

        '''
        first, _ = self.indicesAround(post, n)
        return (first == 0)


    def includesLastPost(self, post, n):
        '''Test if the posts around the given post include the last
        post in the series.

        :param post: the post
        :param n: the number of posts displayed around
        :returns: True if these posts include the first one

        '''
        _, last = self.indicesAround(post, n)
        return (last == self.numberOfPosts() - 1)


class Series(SignalHandler):

    '''Series constructor. This is called when the categories are
    marked by Nikola, and assigns a SeriesRep object to each post that
    is a part of a series.

    '''

    name = "series"

    def orderPosts(self, lang, posts):
        '''Put the posts into order.

        Posts are by default put into order of increasing date. If any
        posts have a 'category_order' metadata value, this is used
        instead. Category orders can be real numbers to allow posts to
        slot into place.

        :param lang: the current language
        :param posts: the posts
        :returns: the posts in sorted order

        '''
        series = []
        for p in posts:
            series.append(p)

        # sort by increasing order of date
        series.sort(key=lambda p: p.meta[lang]['date'])

        # run through the posts and add date ordering to any
        # posts without an explicit position
        for i in range(len(series)):
            if 'category_order' not in series[i].meta[lang].keys():
                series[i].meta[lang]['category_order'] = float(i + 1)

        # sort into category ordering
        series.sort(key=lambda p: float(p.meta[lang]['category_order']))

        # create a representation and return it
        return SeriesRep(series)


    def buildSeries(self, lang, cat, posts):
        '''Build the series from a category.

        :param lang: the current language
        :param cat: the category
        :param posts: the posts in the category

        '''
        series = self.orderPosts(lang, posts)
        for post in posts:
            post.series = series

        # change the next and previous links to be within the
        # series
        # series.inSeriesLinks()


    def buildAllSeries(self, site):
        '''Build all the series, one per category.

        '''
        for lang, langposts in site.posts_per_classification['category'].items():
            for cat, posts in langposts.items():
                self.buildSeries(lang, cat, posts)


    def set_site(self, site):
        '''Set the site.

        This both records the site with the plugin and connects to the
        appropriate signal to reigger series construction.

        :param site: the site (Nikola instance)

        '''
        super().set_site(site)

        # after taxonomies_classifier has set site.posts_per_classification,
        # construct the series
        blinker.signal("taxonomies_classified").connect(self.buildAllSeries)
