===
MDR
===

.. image:: https://travis-ci.org/scrapinghub/mdr.svg?branch=master
    :target: https://travis-ci.org/scrapinghub/mdr

MDR is a library detect and extract listing data from HTML page. It implemented base on the `Finding and Extracting Data Records from Web Pages <http://dl.acm.org/citation.cfm?id=1743635>`_ but
change the similarity to tree alignment proposed by `Web Data Extraction Based on Partial Tree Alignment <http://doi.acm.org/10.1145/1060745.1060761>`_ and `Automatic Wrapper Adaptation by Tree Edit Distance Matching <http://arxiv.org/pdf/1103.1252.pdf>`_.


Requires
========

``numpy`` and ``scipy`` must be installed to build this package.

Usage
=====

Detect listing data
~~~~~~~~~~~~~~~~~~~

MDR assume the data record close to the elements has most text nodes::

    [1]: import requests
    [2]: from mdr import MDR
    [3]: mdr = MDR()
    [4]: r = requests.get('http://www.yelp.co.uk/biz/the-ledbury-london')
    [5]: candidates, doc = mdr.list_candidates(r.text.encode('utf8'))
    ...

    [8]: [doc.getpath(c) for c in candidates[:10]]
     ['/html/body/div[2]/div[3]/div[2]/div/div[1]/div[1]/div[2]/div[1]/div[2]/ul',
     '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]',
     '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/div[2]',
     '/html/body/div[2]/div[3]/div[1]/div/div[4]/div[1]/div/div[1]/div/div[2]/div[1]/div[1]/div',
     '/html/body/div[2]/div[3]/div[1]/div/div[4]/div[2]/div/div[3]',
     '/html/body/div[2]/div[3]/div[1]/div/div[4]/div[1]/div/div[2]/ul/li[2]/div/div/ul',
     '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[1]/div[2]/div[1]',
     '/html/body/div[2]/div[3]/div[2]/div/div[1]/div[2]/div[2]/div[1]/table/tbody',
     '/html/body/div[2]',
     '/html/body/div[2]/div[4]/div/div[1]']

Extract data record
~~~~~~~~~~~~~~~~~~~

MDR can find the repetiton patterns by using tree matching under certain candidate DOM tree, then it builds a mapping from HTML element to other matched elements of the DOM tree.

Used with annotation (optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can annotate the seed elements with any tools (e.g. scrapely_) you like, then mdr will be able to find the other matched elements on the page.

e.g. you can find this demo page here_. the colored data in first row are annotated manually, the rest are extracted by MDR.

Author
======

Terry Peng <pengtaoo@gmail.com>

License
=======

MIT

.. _scrapely: https://github.com/scrapy/scrapely
.. _here: http://ibc.scrapinghub.com/tmp/h.html
