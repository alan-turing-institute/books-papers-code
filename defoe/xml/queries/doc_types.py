"""
Finds every unique document type (DOCTYPE) and its frequency.
"""

from operator import add


def do_query(documents, config_file=None, logger=None):
    """
    Finds every unique document type (DOCTYPE) and its frequency.

    Returns result of form:

        {
          <DOCTYPE>: <COUNT>,
          ...
        }

    :param issues: RDD of defoe.xml.document.Document
    :type issues: pyspark.rdd.PipelinedRDD
    :param config_file: query configuration file (unused)
    :type config_file: str or unicode
    :param logger: logger (unused)
    :type logger: py4j.java_gateway.JavaObject
    :return: unique document types and frequencies
    :rtype: dict
    """
    # [(doc_type, 1), (doc_type, 1), ...]
    doc_types = documents.map(lambda document:
                              (document.doc_type, 1))

    # [(doc_type, 1), (doc_type, 1), ...]
    # =>
    # [(doc_type, count), (doc_type, count), ...]
    doc_type_counts = doc_types. \
        reduceByKey(add). \
        collect()
    return doc_type_counts
