from tools.validate_blog_series_examples import validate


def test_blog_series_method_examples_are_complete():
    assert validate() == []
