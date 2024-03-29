from haystack import indexes
from models import UshahidiReport
import datetime

class UshahididReportIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='user')
    pub_date = indexes.DateTimeField(model_attr='created')

    def get_model(self):
        return UshahidiReport

    def index_queryset(self):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
