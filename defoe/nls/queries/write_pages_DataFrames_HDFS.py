""" 
Pages as string to HDFS CSv files (using dataframes), and some metadata associated with each document.
"""

from defoe import query_utils
from defoe.nls.query_utils import get_page_as_string
from pyspark.sql import Row, SparkSession, SQLContext

import yaml, os

def do_query(archives, config_file=None, logger=None, context=None):
    """
    Writes pages (preprocessed or not) as string to HDFS textfiles, and some metadata associated with each document.
    If we have a config_file indiciating the preprocess treament, it will be to the words extracted from pages. Otherwise, non preprocess treatment will be applied.
    Metadata collected: tittle, edition, year, place, archive filename, page filename, page id, num pages, type of archive, model, type of preprocess treatment, prep_page_string, num_page_words

    Data is saved as Dataframes into HDFS CSV files 


    Example:
    ('Encyclopaedia Britannica; or, A dictionary of arts, sciences, and miscellaneous literature', 'Fourth edition ...', 
      1810, 'Edinburgh', '/mnt/lustre/at003/at003/rfilguei2/nls-data-encyclopaediaBritannica/191253839', 
      'alto/192209952.34.xml', 'Page5', 446, 'book', 'nls', <PreprocessWordType.NONE:4>, u"Part III. MORAL PHILOSOPHY....., '46')
    :param archives: RDD of defoe.nls.archive.Archive
    :type archives: pyspark.rdd.PipelinedRDD
    :param config_file: query configuration file
    :type config_file: str or unicode
    :param logger: logger (unused)
    :type logger: py4j.java_gateway.JavaObject
    :return: "0"
    :rtype: string
    """
    
    if config_file is not None:
        with open(config_file, "r") as f:
            config = yaml.load(f)
    	preprocess_type = query_utils.extract_preprocess_word_type(config)
    else:
        preprocess_type = query_utils.parse_preprocess_word_type("none")
    documents = archives.flatMap(
        lambda archive: [(document.title, document.edition, str(document.year), \
                          document.place, document.archive.filename, str(document.num_pages), \
                           document.document_type, document.model, document) for document in list(archive)])
    # [(tittle, edition, year, place, archive filename, page filename, 
    #   page id, num pages, type of archive, type of disribution, model, type of preprocess treatment, page_as_string)]
    pages = documents.flatMap(
        lambda year_document: [(year_document[0], year_document[1], year_document[2],\
                               year_document[3], year_document[4], page.code, page.page_id, \
                               year_document[5], year_document[6], year_document[7], str(preprocess_type), \
                               get_page_as_string(page, preprocess_type), len(page.words)) for page in year_document[8]])


    nlsRow=Row("title","edition","year", "place", "archive_filename", "page_filename","page_id","num_pages","type_archive","model","preprocess","page_string", "num_page_words")
    sqlContext = SQLContext(context)
    df = sqlContext.createDataFrame(pages,nlsRow)
    if preprocess_type == query_utils.parse_preprocess_word_type("none"):
    	df.write.mode('overwrite').option("header","true").csv("hdfs:///user/at003/rosa/nls_demo_raw.csv")
    else:
    	df.write.mode('overwrite').option("header","true").csv("hdfs:///user/at003/rosa/nls_demo_prep.csv")
    return "0"
