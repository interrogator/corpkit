def corenlp_downloader(custompath=False):
    """
    Very simple CoreNLP downloader

    :param custompath: A path where you want to put CoreNLP
    :type custompath: ``str``

    :Usage:
    python -m corpkit.download.corenlp
    """

    import os
    from corpkit.build import download_large_file
    from corpkit.process import get_corenlp_path
    from corpkit.constants import CORENLP_URL as url

    cnlp_dir = os.path.join(os.path.expanduser("~"), 'corenlp')
    
    corenlppath, fpath = download_large_file(cnlp_dir, url,
                                         actually_download=True,
                                         custom_corenlp_dir=custompath)

if __name__ == '__main__':
    import sys
    custompath = False if len(sys.argv) == 1 else sys.argv[-1]
    corenlp_downloader(custompath=custompath)
    